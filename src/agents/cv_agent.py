import logging
from datetime import datetime
from typing import Any

from langchain.prompts import SystemMessagePromptTemplate
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import (
    Runnable,
    RunnableConfig,
    RunnableLambda,
    RunnableSerializable,
)
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.store.base import BaseStore
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from core import get_model, settings

# Added logger
logger = logging.getLogger(__name__)


class AgentState(MessagesState, total=False):
    """`total=False` is PEP589 specs.

    documentation: https://typing.readthedocs.io/en/latest/spec/typeddict.html#totality
    """

    birthdate: datetime | None


def wrap_model(
    model: BaseChatModel | Runnable[LanguageModelInput, Any], system_prompt: BaseMessage
) -> RunnableSerializable[AgentState, Any]:
    preprocessor = RunnableLambda(
        lambda state: [system_prompt] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | model


async def question_1(state: AgentState, config: RunnableConfig) -> AgentState:

    question_1_input = interrupt("What is your favourite dinosaur?")
    # Re-run extraction with the new input
    return {"messages": [HumanMessage(question_1_input)]}


async def comment_1(state: AgentState, config: RunnableConfig) -> AgentState:
    """This node is to demonstrate doing work before the interrupt"""

    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))

    background_prompt = SystemMessagePromptTemplate.from_template(
        """
    Provide some facts about the dinosaur the user indicated. 
    """
    )

    model_runnable = wrap_model(m, background_prompt.format())
    response = await model_runnable.ainvoke(state, config)
    print(response)
    return {"messages": [AIMessage(content=response.content)]}


async def question_2(state: AgentState, config: RunnableConfig) -> AgentState:

    question_2_input = interrupt("What is your favourite food?")
    # Re-run extraction with the new input
    return {"messages": [HumanMessage(question_2_input)]}


async def comment_2(state: AgentState, config: RunnableConfig) -> AgentState:
    """This node is to demonstrate doing work before the interrupt"""

    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))

    background_prompt = SystemMessagePromptTemplate.from_template(
        """
    Provide some facts about the food the user indicated. 
    """
    )

    model_runnable = wrap_model(m, background_prompt.format())
    response = await model_runnable.ainvoke(state, config)
    print(response)
    return {"messages": [AIMessage(content=response.content)]}


# Define the graph
agent = StateGraph(AgentState)
agent.add_node("question_1", question_1)
agent.add_node("comment_1", comment_1)
agent.add_node("question_2", question_2)
agent.add_node("comment_2", comment_2)

agent.set_entry_point("question_1")
agent.add_edge("question_1", "comment_1")
agent.add_edge("comment_1", "question_2")
agent.add_edge("question_2", "comment_2")
agent.add_edge("comment_2", END)

cv_agent = agent.compile()
cv_agent.name = "cv-agent"
