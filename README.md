# MiniPilot

This application implements a chatbot you can train with your data. From the GUI you will be able to:

- Upload CSV data
- Create an index
- Edit the system and user prompt
- Ask questions in natural language

![demo](src/static/images/minipilot.gif)

The system uses:

- Redis Stack as a Vector Database to store the dataset and vectorize the entries to perform [Vector Similarity Search (VSS)](https://redis.io/docs/latest/develop/interact/search-and-query/advanced-concepts/vectors/) for RAG
- OpenAI ChatGPT Large Language Model (LLM) [ChatCompletion API](https://platform.openai.com/docs/guides/gpt/chat-completions-api)

## Requirements

First, [create your OpenAI token](https://platform.openai.com/docs/quickstart). 

Then, decide where you want to run your Redis Stack instance.

- Create a free 30MB [Redis Cloud subscription](https://redis.io/try-free/)
- Install Redis Stack [on your laptop](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/)
- Run a [Redis Stack Docker container](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/). 

## Docker setup

Once you have your OpenAI token and a Redis Stack database available, pull the [MiniPilot container](https://hub.docker.com/r/ortolano/minipilot) and run it.

```commandline
docker run -d --cap-add sys_resource --env DB_SERVICE="host.docker.internal" --env DB_PORT=6379 --env DB_PWD="your-redis-password" --env DB_SSL="True" --env OPENAI_API_KEY="your-openai-key" --env MINIPILOT_ENDPOINT="http://127.0.0.1:8000" --name minipilot -p 5007:8000 ortolano/minipilot:0.1
```

Explanation of the environment follows.

```commandline
DB_SERVICE             The IP address of your Redis Stack instance or the hostname of a Redis Cloud database. If Redis Stack runs on your host, you can connect to the Docker host from the Docker container using "host.docker.internal"
DB_PORT                The port of your Redis Stack instance or Redis Cloud database
DB_PWD                 The password of your Redis Stack instance or Redis Cloud database
DB_SSL                 If you would like to connect using SSL (mandatory for Redis Cloud databases)
OPENAI_API_KEY         Your OpenAI token
MINIPILOT_ENDPOINT     MiniPilot is a REST API service, but the internal chat interface uses the REST API, too, on the default exposed port 8000. You can just leave http://127.0.0.1:8000
```

## Local setup

If you prefer to run MiniPilot on your laptop, just clone the repository.

```commandline
git clone https://github.com/mortensi/MiniPilot.git
```

Install the requirements in a Python virtual environment

```commandline
python3 -m venv minipilot
source minipilot/bin/activate

cd minipilot
pip install -r requirements.txt
```

Then set the environment variables in a `.env` file. Note that the software leverages the embedded REST API Server, then  configure the variable MINIPILOT_ENDPOINT="http://localhost:5005" or using the desired port.

```commandline
DB_SERVICE="127.0.0.1"
DB_PORT=6379
DB_PWD=""

MINIPILOT_DEBUG = "True"
MINIPILOT_MODEL="gpt-3.5-turbo-16k"
MINIPILOT_ENDPOINT="http://localhost:5005"

OPENAI_API_KEY="your-openai-key"
```

You can also use the `export` command.

```commandline
export DB_SERVICE="127.0.0.1" DB_PORT=6379 DB_PWD="" MINIPILOT_DEBUG="True" MINIPILOT_MODEL="gpt-3.5-turbo-16k" MINIPILOT_ENDPOINT="http://localhost:5005" OPENAI_API_KEY="your-openai-key"
```

Start the server. 

> The first time, it may take up to two minutes: heavy embedding models will be downloaded.

```
./start.sh
```

## Configuring MiniPilot

1. point your browser to [http://127.0.0.1:5005/](http://127.0.0.1:5005/)
2. From the `data` tab, load a CSV dataset, and index it. You can try the [IMDB movies dataset](https://www.kaggle.com/datasets/ashpalsingh1525/imdb-movies-dataset)
3. From the `prompts` tab, edit the system and user prompts and save them
4. Start asking!


## Rest API server

Consult the Swagger REST API documentation at [http://127.0.0.1:5005/api](http://127.0.0.1:5005/api).

The following endpoints deliver the chat, history, references and conversation reset services. 

```
curl -X POST 'http://127.0.0.1:5007/api/chat?q=suggest%20a%20horror%movie' -H 'accept: application/json' -H 'session-id: my-session-id'

curl -X GET 'http://127.0.0.1:5007/api/history' -H 'accept: application/json' -H 'session-id: my-session-id'

curl -X GET 'http://127.0.0.1:5007/api/references?q=recommend%20a%20movie' -H 'accept: application/json'

curl -X 'POST' 'http://127.0.0.1:5007/api/reset' -H 'accept: application/json' -H 'session-id: my-session-id'
```
