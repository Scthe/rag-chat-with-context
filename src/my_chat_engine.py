import asyncio
from typing import List, Optional, Tuple
from threading import Thread
from termcolor import colored

from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.callbacks import trace_method
from llama_index.core.schema import MetadataMode, NodeWithScore
from llama_index.core.chat_engine.types import (
    StreamingAgentChatResponse,
    ToolOutput,
)
from llama_index.core.chat_engine import CondensePlusContextChatEngine

from src.model_prompts import BaseTemplateFormatter, get_template_formatter


class Event_ts(asyncio.Event):
    def set(self):
        self._loop.call_soon_threadsafe(super().set)


class MyCondensePlusContextChatEngine(CondensePlusContextChatEngine):
    """Fix for `llama_index.core.chat_engine.CondensePlusContextChatEngine`

    It uses threading incorrectly. It calls `Event.set()` from different thread,
    which is verboten(). We replace the `asyncio.Event` with our own
    thread-safe version to fix it.

    @see https://stackoverflow.com/questions/33000200/asyncio-wait-for-event-from-other-thread
    @see https://stackoverflow.com/questions/48836285/python-asyncio-event-wait-not-responding-to-event-set
    """

    @trace_method("chat")
    async def astream_chat(
        self, message: str, chat_history: Optional[List[ChatMessage]] = None
    ) -> StreamingAgentChatResponse:
        # TODO remove from config? or use here to clip the chat history to right length
        # if chat_history is not None:
        # self._memory.set(chat_history)
        # chat_history = self._memory.get()
        fmt_template = get_template_formatter(self._llm.model)

        condensed_question = await self._arephrase_question(
            fmt_template, chat_history, message
        )
        if self._verbose:
            print(
                colored(f"Raw condensed question:", "blue"), f"'{condensed_question}'"
            )
        condensed_question = fmt_template.parse_standalone_question_answer(
            condensed_question
        )
        if self._verbose:
            print(
                colored(f"Final condensed question:", "blue"), f"'{condensed_question}'"
            )

        context_full_text, context_nodes = await self._afind_matching_chunks(
            condensed_question
        )
        if self._verbose:
            sources = [
                x.node.metadata.get("filename", "<Unknown source>")
                for x in context_nodes
            ]
            print(colored(f"Sources", "blue"), sources)

        chat_messages = fmt_template.prompt_summarize_paragraphs_for_answer(
            self._context_prompt_template, context_full_text, condensed_question
        )
        if self._verbose:
            for i, ch_msg in enumerate(chat_messages):
                print(colored(f"chat_message.{i}:", "blue"), ch_msg)

        # pass the context, system prompt and user message as chat to LLM to generate a response
        context_source = ToolOutput(
            tool_name="retriever",
            content=context_full_text,
            raw_input={"message": condensed_question},
            raw_output=context_full_text,
        )
        chat_response = StreamingAgentChatResponse(
            achat_stream=await self._llm.astream_chat(chat_messages),
            sources=[context_source],
            source_nodes=context_nodes,
        )
        chat_response._new_item_event = Event_ts()  # FIX

        # This thread is done cause we don't want to `await` here
        thread = Thread(
            target=lambda x: asyncio.run(chat_response.awrite_response_to_history(x)),
            args=(self._memory,),
        )
        thread.start()

        return chat_response, condensed_question

    async def _arephrase_question(
        self,
        fmt_template: BaseTemplateFormatter,
        chat_history: List[ChatMessage],
        latest_message: str,
    ) -> str:
        """Given chat history and user's question, rephrase the question to fill data from chat context"""
        if len(chat_history) == 0:
            return latest_message

        llm = self._llm
        tmpl = self._condense_prompt_template
        prompt = fmt_template.prompt_standalone_question(
            tmpl, chat_history, latest_message
        )

        if self._verbose:
            print(
                colored(f"Condensing question using prompt:\n", "blue"),
                f'{prompt}\n{"*"*10}',
            )
        response = await llm.acomplete(prompt, formatted=True)
        return response.text.rstrip()

    async def _afind_matching_chunks(
        self, message: str
    ) -> Tuple[str, List[NodeWithScore]]:
        nodes = await self._retriever.aretrieve(message)
        context_str = "\n\n".join(
            [n.node.get_content(metadata_mode=MetadataMode.LLM).strip() for n in nodes]
        )
        return context_str, nodes

    """
    def log_partial_processing_output(
        self, chat_messages, context_source, context_nodes
    ):
        print("*" * 5, "CONDENSED QUESTION, CONTEXT, SOURCES", "*" * 5)
        print(
            colored(f"condensed_question:", "blue"),
            f'"{context_source.raw_input}"',
        )
        for i, ch_msg in enumerate(chat_messages):
            print(colored(f"chat_message.{i}:", "blue"), ch_msg)

        sources = [
            x.node.metadata.get("filename", "<Unknown source>") for x in context_nodes
        ]
        print(colored(f"Sources", "blue"), sources)
        # print(colored(f'context_source="{context_source}"', "yellow"))
        # print(colored(f'context_nodes="{context_nodes}"', "red"))
        print("*" * 20)
    """
