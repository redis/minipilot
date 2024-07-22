# Frequently Asked Questions

## What is this?

MiniPilot is a GenAI-assisted chatbot. This demo is a minimal implementation (hence the name "MiniPilot"!) which allows you to import data as CSV, process it and store it in a Redis vector database.
You can clone and test the repository, fork it, change the code and, if you like, contribute to the repository. It can be extended to import data from other document formats (like PDF) or crawl and scrape web resources. Ad-hoc connectors can be developed to extend the MiniPilot.

## What features can I find in MiniPilot?

MiniPilot supports:

- Conversation history by session, to make sense of the interactions of a user
- Semantic cache, to store and retrieve past interactions (from all the conversations of all the users). This speeds up the system, because if an answer is in the cache, there is no need to invoke the OpenAI chat endpoint at all.
- Rate limiter, a basic implementation based on Redis
- Configurability, to tune up every single piece of the chatbot
- REST API: the MiniPilot can serve remote users over a REST API. The UI is for demonstrative purposes. 
- Centralized Redis session, so application servers are purely stateless, which helps scalability of the service

## What can I do with MiniPilot?

You can use the code for self-learning, extend it as desired and use in production. The source code sheds light on all the standard components used in these kinds of systems:

- Streaming results from OpenAI back to the client
- Asynchronous streaming to the user and rendering in the browser
- REST API server, with the standard Swagger documentation
- Ready to be used as a Docker container in K8s clusters, Dockerfile is ready to use
- Central Redis session management, which enables stateless containers for dynamic scalability of the service