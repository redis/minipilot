# MiniPilot

This application implements a chatbot you can train with your data. The example provided is a movie recommender system.

![demo](src/static/images/minipilot.gif)

The system uses:

- Redis Stack as a Vector Database to store the dataset and vectorize the entries to perform [Vector Similarity Search (VSS)](https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/vectors/) for RAG
- The [IMDB movies dataset](https://www.kaggle.com/datasets/ashpalsingh1525/imdb-movies-dataset), which contains 10000+ movies from the IMDB Movies dataset
- OpenAI ChatGPT Large Language Model (LLM) [ChatCompletion API](https://platform.openai.com/docs/guides/gpt/chat-completions-api)

## setup

Clone the repository 

```commandline
git clone https://github.com/mortensi/MiniPilot.git
```

Make sure you have an [OpenAI token](https://openai.com/api/pricing/), then install the requirements in a Python virtual environment

```commandline
python3 -m venv minipilot
source minipilot/bin/activate

cd minipilot
pip install -r requirements.txt
```

Then set the environment variables in a `.env` file.

```commandline
DB_SERVICE="127.0.0.1"
DB_PORT=6379
DB_PWD=""

MINIPILOT_DEBUG = "True"
MINIPILOT_MODEL="gpt-3.5-turbo-16k"

OPENAI_API_KEY="your-openai-key"
```

You can also use the `export` command.

```commandline
export DB_SERVICE="127.0.0.1" DB_PORT=6379 DB_PWD="" MINIPILOT_DEBUG="True" MINIPILOT_MODEL="gpt-3.5-turbo-16k" OPENAI_API_KEY="your-openai-key"
```

Start the server. 

> The first time, it may take up to two minutes: heavy embedding models will be downloaded.

```
./start.sh
```

Load the database.

> This is uploading 10,000 movies, it may take up to 20 minutes

```
python3 initialize.sh
```

Complete the installation by

1. Pointing your browser to [http://127.0.0.1:5005/](http://127.0.0.1:5005/)
2. From the `status` tab, make the new index current
3. Start asking!


## Rest API server

Consult the Swagger REST API documentation at [http://127.0.0.1:5005/api](http://127.0.0.1:5005/api).

The following endpoints deliver the chat, history, references and conversation reset services. 

```
curl -X POST 'http://127.0.0.1:5005/api/chat?q=suggest%20a%20horror%movie' -H 'accept: application/json' -H 'session-id: my-session-id'

curl -X GET 'http://127.0.0.1:5005/api/history' -H 'accept: application/json' -H 'session-id: my-session-id'

curl -X GET 'http://127.0.0.1:5005/api/references?q=recommend%20a%20movie' -H 'accept: application/json'

curl -X 'POST' 'http://127.0.0.1:5005/api/reset' -H 'accept: application/json' -H 'session-id: my-session-id'
```
