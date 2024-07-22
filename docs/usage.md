# Usage

MiniPilot is a highly configurable server. Read the environment variables to customize the server's behavior.

| Variable                            | Description                                                                                                                    | Default           |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `OPENAI_API_KEY`                    | This is the OpenAI token.                                                                                                      |                   |
| `OPENAI_MODEL`                      | You can specify the desired LLM.                                                                                               | `gpt-4o-mini`     |
| `DB_SERVICE`                        | Redis IP or hostname.                                                                                                          | `127.0.0.1`       |
| `DB_PORT`                           | Redis port.                                                                                                                    | `6379`            |
| `DB_PWD`                            | Redis password.                                                                                                                |                   |
| `MINIPILOT_DEBUG`                   | It enables the debugging mode.                                                                                                 | `True`            |
| `MINIPILOT_LOG`                     | Where the log file will be saved.                                                                                              | `./minipilot.log` |
| `MINIPILOT_ENDPOINT`                | The UI invokes the local REST API, provide an endpoint like `http://localhost:5005`.                                           |                   |
| `MINIPILOT_HISTORY_TIMEOUT`         | Time to Live of the entries in the conversation history.                                                                       | `604800`          |
| `MINIPILOT_HISTORY_LENGTH`          | The conversation history is limited, when the max configured number of interactions is reached, the older entries are removed. | `30`              |
| `MINIPILOT_RATE_LIMITER_ENABLED`    | Whether the rate limiter is enabled.                                                                                           | `True`            |
| `MINIPILOT_RATE_LIMITER_CRITERIA`   | Limiting the rate based on `ip` , `session`, or `all`.                                                                         | `session`         |
| `MINIPILOT_RATE_LIMITER_ALLOW`      | Maximum operations per minute allowed by the rate limiter.                                                                     | `10`              |
| `MINIPILOT_CONVERSATION_LENGTH`     | Maximum size of the `minipilot:conversation` stream storing all the interactions.                                              | `10000`           |
| `MINIPILOT_LOG_LENGTH`              | Maximum size of the `minipilot:log` stream storing the application log.                                                        | `1000`            |
| `MINIPILOT_CONTEXT_LENGTH`          | Number of entries retrieved from the database for RAG.                                                                         | `5`               |
| `MINIPILOT_CONTEXT_RELEVANCE_SCORE` | Threshold to limit the returned entries retrieved from the database for RAG.                                                   | `0.78`            |
| `MINIPILOT_LLM_TIMEOUT`             | Timeout to control eventual LLM slowness.                                                                                      | `10`              |
| `MINIPILOT_CACHE_TTL`               | Time to Live of the entries in the semantic cache.                                                                             | `3600 * 24 * 30`  |
| `MINIPILOT_CACHE_THRESHOLD`         | Semantic similarity threshold for the results retrieved from the semantic cache.                                               | `0.1`             |
| `MINIPILOT_CACHE_ENABLED`           | Whether the semantic cache is enabled.                                                                                         | `True`            |