from typing import cast, Literal
from langchain_anthropic import ChatAnthropic
from IPython.display import Image, display
from langgraph.graph import StateGraph, END
from src.utils.pymodels import ChatRequest, ChatResponse
from src.agent_prompt.code_fix_agent import get_fix_user_prompt
from src.utils.common import logger, make_orch_output, ChatOrchestratorState
from src.agent_prompt.classifier import make_system_prompt, get_user_prompt


class ChatOrchestrator:
    """Orchestrates the chat flow with a classifier → fixer hierarchy."""

    def __init__(self):
        self.request: ChatRequest = None
        self.llm = ChatAnthropic(model="claude-sonnet-4-20250514")
        self.compile()

    # --------- nodes ---------

    def classifier_node(self, state: ChatOrchestratorState):
        """Step 1: classify vulnerability"""
        sys_prompt = make_system_prompt()
        output = self.llm.invoke([sys_prompt] + state["messages"])
        logger.info("**Classifier output** %s - %s", self.request.title, output.content)
        return {"messages": [output]}

    def fixer_node(self, state: ChatOrchestratorState):
        """Step 2: apply fix using classifier output"""
        class_category = state["messages"][-1].content
        fix_input = get_fix_user_prompt(
            class_category,
            self.request,
        )
        output = self.llm.invoke([fix_input])
        logger.info("**Fixer output** %s - %s", self.request.title, output.content)

        return {"messages": [output]}

    def condition_node(self, state: ChatOrchestratorState) -> Literal["fixer", END]:
        """Decide whether to run fixer based on classifier output"""
        invalid = {None, "", "n/a"}
        if self.request.codebase in invalid or self.request.title in invalid:
            return END
        return "fixer"

    # --------- graph ---------

    def compile(self):
        """Compile the state graph for the chat orchestrator."""
        builder = StateGraph(ChatOrchestratorState)

        builder.add_node("classifier", self.classifier_node)
        builder.add_node("fixer", self.fixer_node)

        builder.set_entry_point("classifier")
        builder.add_conditional_edges("classifier", self.condition_node)

        self.graph = builder.compile()

    def show_graph(self):
        """Render the state graph"""
        try:
            png_data = self.graph.get_graph(xray=True).draw_mermaid_png()
            display(Image(png_data))
        except Exception as e:
            logger.error("Failed to render graph image: %s", e)
            logger.info(self.graph.get_graph(xray=True).draw_mermaid())

    def invoke(self, request: ChatRequest) -> ChatResponse:
        """Run classifier → fixer pipeline"""
        self.request = request
        reply: ChatOrchestratorState = cast(
            ChatOrchestratorState,
            self.graph.invoke({"messages": [get_user_prompt(request)]}),
        )
        return make_orch_output(reply, request)
