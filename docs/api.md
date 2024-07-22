# REST API

Consult the Swagger REST API documentation at [http://127.0.0.1:5005/api](http://127.0.0.1:5005/api).

The following endpoints deliver the chat, history, references and conversation reset services.

## Chat

This is the relevant endpoint to ask questions. Provide a session ID so the conversation history is maintained and used throughout the interaction.

```
curl -X POST 'http://127.0.0.1:5007/api/chat?q=suggest%20a%20horror%movie' -H 'accept: application/json' -H 'session-id: my-session-id'
```

## History

Keyed by session ID, this endpoint returns the interactions with the chatbot. Useful for rendering it in a UI. To be invoked on page refresh, for example.

```
curl -X GET 'http://127.0.0.1:5007/api/history' -H 'accept: application/json' -H 'session-id: my-session-id'
```

## References

This endpoint delivers semantically relevant results. Not a bot interaction, but a useful semantic recommender system.

```
curl -X GET 'http://127.0.0.1:5007/api/references?q=recommend%20a%20movie' -H 'accept: application/json'
```

## Reset history

When conversations are too long, the chatbot may incur into less than precise results. Cleaning up the history restarts the conversation from scratch.

```
curl -X 'POST' 'http://127.0.0.1:5007/api/reset' -H 'accept: application/json' -H 'session-id: my-session-id'
```