import csv
import os
from datetime import datetime
import logging

import redis
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.redis import Redis


def generate_redis_connection_string():
    if os.getenv('DB_PWD', ''):
        connection_string = f"redis://:{os.getenv('DB_PWD', '')}@{os.getenv('DB_SERVICE', '127.0.0.1')}:{int(os.getenv('DB_PORT', 6379))}"
    else:
        connection_string = f"redis://{os.getenv('DB_SERVICE', '127.0.0.1')}:{int(os.getenv('DB_PORT', 6379))}"

    return connection_string


def load():
    conn = redis.from_url(generate_redis_connection_string())

    # Create a new index
    index_name = f"minipilot_rag_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}_idx"

    index_schema = {
        "tag": [{"name": "genre"},
                {"name": "country"}],
        "text": [{"name": "names"}],
        "numeric": [{"name": "revenue"},
                    {"name": "score"},
                    {"name": "date_x"}]
    }

    vector_schema = {
        "algorithm": "HNSW"
    }

    # If there is no index for RAG, this is the first index; then, manually point an alias to it
    try:
        conn.ft('convai_rag_alias').info()
    except redis.exceptions.ResponseError as e:
        logging.warning(f"No alias exists for semantic search. Create the alias when indexing is done")

    # Validate there is an OPENAI_API_KEY passed in the environment
    try:
        embedding_model = OpenAIEmbeddings()
    except Exception as e:
        logging.error(e)
        return

    doc_splitter = RecursiveCharacterTextSplitter(  chunk_size=10000,
                                                    chunk_overlap=50,
                                                    length_function=len,
                                                    add_start_index=True
                                                    )

    with open("imdb_movies.csv", encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        cnt = 0
        for row in csvReader:
            movie = f"movie title is: {row['names']}\n"
            movie += f"movie genre is: {row['genre']}\n"
            movie += f"movie crew is: {row['crew']}\n"
            movie += f"movie score is: {row['score']}\n"
            movie += f"movie overview is: {row['overview']}\n"
            movie += f"movie country is: {row['country']}\n"
            movie += f"movie revenue is: {row['revenue']}\n"


            cnt += 1
            splits = doc_splitter.split_text(row['overview'])
            unix_timestamp = int(datetime.strptime(row['date_x'].strip(), "%m/%d/%Y").timestamp())
            metadatas = {"names": row['names'],
                         "genre": row['genre'],
                         "country": row['country'],
                         "revenue": row['revenue'],
                         "score": row['score'],
                         "date_x": unix_timestamp}

            if len(splits) > 0:
                Redis.from_texts(texts=splits,
                                 metadatas=[metadatas] * len(splits),
                                 embedding=embedding_model,
                                 index_name=index_name,
                                 index_schema=index_schema,
                                 vector_schema=vector_schema,
                                 redis_url=generate_redis_connection_string())

load()
