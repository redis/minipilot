# Installation

Read along to learn how to set up a Redis Stack instance and start the server.

## Requirements

First, [create your OpenAI token](https://platform.openai.com/docs/quickstart). 

Then, decide where you want to run your Redis Stack instance.

- Create a free 30MB [Redis Cloud subscription](https://redis.io/try-free/)
- Install Redis Stack [on your laptop](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/)
- Run a [Redis Stack Docker container](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/docker/). 


## Local setup

To run MiniPilot on your laptop, just clone the repository.

```commandline
git clone https://github.com/redis/MiniPilot.git
```

Install the requirements in a Python virtual environment

```commandline
python3 -m venv minipilot
source minipilot/bin/activate

cd minipilot
pip install -r requirements.txt
```

Then set the environment variables in a `.env` file. Note that the functions used through the UI leverage the embedded REST API Server, then configure the variable MINIPILOT_ENDPOINT="http://localhost:5005". Specify the desired port.

```commandline
DB_SERVICE="127.0.0.1"
DB_PORT=6379
DB_PWD=""

MINIPILOT_DEBUG = "True"
MINIPILOT_ENDPOINT="http://localhost:5005"

OPENAI_API_KEY="your-openai-key"
OPENAI_MODEL="gpt-4o-mini"
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

## Docker setup

Once you have your OpenAI token and a Redis Stack database available, you can create your Docker image using the provided `Dockerfile`.

```commandline
docker build --no-cache -t minipilot:0.1 .
```

Once the image has been added to your local repository, start the container.

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

## Configuring MiniPilot

1. point your browser to [http://127.0.0.1:5005/](http://127.0.0.1:5005/)
2. From the `data` tab, load a CSV dataset, and index it. You can try the [IMDB movies dataset](https://www.kaggle.com/datasets/ashpalsingh1525/imdb-movies-dataset)
3. From the `prompts` tab, edit the system and user prompts and save them
4. Start asking!