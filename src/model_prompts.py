import re
from abc import ABC, abstractmethod

from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.base.llms.generic_utils import messages_to_history_str
from llama_index.core.prompts.base import PromptTemplate


LLM_GEMMA = "gemma:2b"
LLM_PHI = "phi"

PHI_TEMPLATE = """Instruct:
{text}
Output:"""

GEMMA_TEMPLATE = """<start_of_turn>user
{text}<end_of_turn>
<start_of_turn>model"""


def wrap_in_prompt(model_name, text, **kwargs):
    text = text.strip()
    # nl = "-" * 10
    # print(f"{nl}{text}{nl}")

    if model_name == LLM_GEMMA:
        return GEMMA_TEMPLATE.format(text=text, **kwargs)
    elif model_name == LLM_PHI:
        return PHI_TEMPLATE.format(text=text, **kwargs)
    else:
        raise Exception(f"Unrecognised LLM model: '{model_name}'")


class BaseTemplateFormatter(ABC):
    @abstractmethod
    def prompt_standalone_question(self) -> None:
        """"""

    @abstractmethod
    def parse_standalone_question_answer(self) -> None:
        """"""

    @abstractmethod
    def prompt_summarize_paragraphs_for_answer(self) -> None:
        "pass"


class TemplateFormatterGemma(BaseTemplateFormatter):
    def prompt_standalone_question(self, template, chat_history, question):
        chat_history_str = messages_to_history_str(chat_history)
        task_str = template.format(chat_history=chat_history_str, question=question)
        return wrap_in_prompt(LLM_GEMMA, task_str)

    def parse_standalone_question_answer(self, rephrased_question):
        # Look for:
        # **Rephrased question:** What is something?
        GEMMA_REPHRASED = "question"
        q_lc = rephrased_question.lower()
        if GEMMA_REPHRASED in q_lc:
            st_idx = q_lc.find(GEMMA_REPHRASED) + len(GEMMA_REPHRASED)
            st_idx = max(st_idx, q_lc.rfind(":"))
            rephrased_question = rephrased_question[st_idx:]
            rephrased_question = re.sub(
                r"^[\W]+", "", rephrased_question
            )  # skip till letters
            rephrased_question = rephrased_question.strip()
        return rephrased_question

    def prompt_summarize_paragraphs_for_answer(
        self, template: PromptTemplate, context_str: str, question: str
    ):
        """Gemma does not have 'system' role. Reformat the chat history for this"""
        msg_text = template.format(context_str=context_str, question=question)
        msg_text = wrap_in_prompt(LLM_GEMMA, msg_text)
        chat_msg = ChatMessage(role="user", content=msg_text)
        return [chat_msg]


class TemplateFormatterPhi(BaseTemplateFormatter):
    def prompt_standalone_question(self, template, chat_history, question):
        chat_history_str = messages_to_history_str(chat_history)
        task_str = template.format(chat_history=chat_history_str, question=question)
        return wrap_in_prompt(LLM_PHI, task_str)

    def parse_standalone_question_answer(self, rephrased_question):
        return rephrased_question

    def prompt_summarize_paragraphs_for_answer(
        self, template: PromptTemplate, context_str: str, question: str
    ):
        msg_text = template.format(context_str=context_str, question=question)
        msg_text = wrap_in_prompt(LLM_PHI, msg_text)
        chat_msg = ChatMessage(role="user", content=msg_text)
        return [chat_msg]


def get_template_formatter(model_name) -> BaseTemplateFormatter:
    if model_name == LLM_GEMMA:
        return TemplateFormatterGemma()
    elif model_name == LLM_PHI:
        return TemplateFormatterPhi()
    else:
        raise Exception(f"Unrecognised LLM model: '{model_name}'")
