import traceback
from typing import Optional
from llama_index.core.callbacks import CallbackManager
from llama_index.core import VectorStoreIndex
from llama_index.core.llms import ChatMessage, MessageRole

from src.config import AppConfig
from src.rag import ask_question_in_chat_async, create_chat_engine


class SocketMsgHandler:
    def __init__(
        self,
        cfg: AppConfig,
        index: VectorStoreIndex,
        callback_manager: Optional[CallbackManager] = None,
    ):
        self.cfg = cfg
        self.index = index
        self.callback_manager = callback_manager
        self.message_history = []

    def create_per_socket_ctx(self):
        """Done, so each socket has own message history"""
        return create_chat_engine(
            self.cfg,
            self.index,
            self.callback_manager,
        )

    async def __call__(self, socket_ctx, msg, ws_send_json):
        msg_id = msg.get("msgId", "")
        type = msg.get("type", "")
        chat_engine = socket_ctx

        try:
            if type == "query":
                await self.ask_question(chat_engine, msg_id, msg, ws_send_json)
            elif type == "reset-context":
                self.reset_context(chat_engine)

        except Exception as e:
            traceback.print_exception(e)
            data = {
                "type": "error",
                "msgId": msg_id,
                "error": str(e),
            }
            await ws_send_json(data)

    async def ask_question(self, chat_engine, msg_id, msg, ws_send_json):
        q = msg.get("text", "")
        answer = ""

        async def on_complete(elapsed, sources, inferred_question):
            self.add_message(MessageRole.USER, inferred_question)
            self.add_message(MessageRole.ASSISTANT, answer)

            data = {
                "type": "done",
                "msgId": msg_id,
                "elapsed": elapsed,
                "sources": sources,
                "inferred_question": inferred_question,
            }
            # print(data)
            await ws_send_json(data)

        async_resp = ask_question_in_chat_async(
            chat_engine, q, self.message_history, on_complete
        )
        async for token in async_resp:
            answer += token
            data = {"type": "token", "msgId": msg_id, "token": token}
            await ws_send_json(data)

    def add_message(self, role, content):
        msg = ChatMessage(content=content, role=role)
        self.message_history.append(msg)

    def reset_context(self, chat_engine):
        chat_engine.reset()
        self.message_history = []
