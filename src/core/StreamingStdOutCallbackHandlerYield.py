import queue
import sys
from typing import Any, Dict, List, Union

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import LLMResult
from openai import BadRequestError

STOP_ITEM = "[END]"


class StreamingStdOutCallbackHandlerYield(StreamingStdOutCallbackHandler):
    q: queue.Queue

    def __init__(self, q: queue.Queue) -> None:
        super().__init__()
        self.q = q

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        with self.q.mutex:
            self.q.queue.clear()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM tokens. Only available when streaming is enabled."""
        # Writes to stdout
        # sys.stdout.write(tokens)
        # sys.stdout.flush()
        # Pass the tokens to the generator
        self.q.put(token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        self.q.put(STOP_ITEM)
        #print(list(self.q.queue))

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt, BadRequestError], **kwargs: Any
    ) -> None:
        """Run when LLM errors."""
        sys.stdout.write("on_llm_error")
        sys.stdout.flush()
        self.q.put("%s: %s" % (type(error).__name__, str(error)))
        self.q.put(STOP_ITEM)

    def notify(self, message: str) -> None:
        self.q.put(message)
        self.q.put(STOP_ITEM)

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        sys.stdout.write("on_tool_error")
        sys.stdout.flush()

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""
        sys.stdout.write("on_chain_error")
        sys.stdout.flush()