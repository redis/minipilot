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

## Documentation
- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [API Documentation](docs/api.md)
- [Architecture Overview](docs/architecture.md)
- [FAQ](docs/faq.md)


