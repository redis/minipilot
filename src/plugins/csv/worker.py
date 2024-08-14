import csv
from datetime import datetime
import logging

import redis
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.redis import Redis

from src.common.config import REDIS_CFG
from src.common.utils import generate_redis_connection_string, get_filename_without_extension


def csv_loader_task(filename):

    # Fail fast: validate there is an OPENAI_API_KEY passed in the environment
    try:
        embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    except Exception as e:
        logging.error(e)


    # Instantiate chunking:
    # max input is 8191 tokens
    # 1 token ~= 4 chars in English
    # 8191 x 4 = 32764 maximum characters that can be represented by a vector embedding
    doc_splitter = RecursiveCharacterTextSplitter(  chunk_size=10000,
                                                    chunk_overlap=50,
                                                    length_function=len,
                                                    add_start_index=True
                                                    )

    # Details for new new Redis vector index, named by CSV file and datetime, using HSNW
    index_name = f"minipilot_rag_{get_filename_without_extension(filename)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_idx"
    index_schema = None
    vector_schema = {
        "algorithm": "HNSW"
    }

    # There are many strategies to index a CSV, for the benefit of simplicity,
    # here we convert a dictionary to a string representation where each key-value pair is on a separate line and formatted as key: value
    # 
    # So for each row
    # columnname1:rowxvalue1\n columnname2:rowxvalue2\n 
    with open(filename, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:
            row_str = '\n'.join([f"{key}: {value}" for key, value in row.items()])
            splits = doc_splitter.split_text(row_str)
            metadatas = None

            if len(splits) > 0:
                # Ingest the document
                Redis.from_texts(texts=splits,
                                 metadatas=metadatas,
                                 embedding=embedding_model,
                                 index_name=index_name,
                                 index_schema=index_schema,
                                 vector_schema=vector_schema,
                                 redis_url=generate_redis_connection_string(REDIS_CFG["host"], REDIS_CFG["port"], REDIS_CFG["password"]))


    # If there is no index for RAG, this is the first index; then, we want to warnthe user should to make it current from the UI
    conn = redis.StrictRedis(host=REDIS_CFG["host"], port=REDIS_CFG["port"], password=REDIS_CFG["password"])
    try:
        conn.ft('minipilot_rag_alias').info()
    except redis.exceptions.ResponseError as e:
        logging.warning(f"No alias exists for semantic search. Associate the alias to the desired index")
