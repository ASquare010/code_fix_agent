from typing import List
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from src.utils.pymodels import ChatRequest, Vulnerability
from src.utils.common import SYS_PROMPTS
from src.utils.common import vulnerabilities


def make_system_prompt() -> SystemMessage:
    """Create the system prompt for the orchestrator agent."""
    return SystemMessage(
        content=PromptTemplate(
            input_variables=[],
            template=SYS_PROMPTS["classifier"],
        ).format()
    )


def get_user_prompt(request: ChatRequest) -> HumanMessage:
    """Create a user prompt message."""

    code_data = "## No codebase provided.\nVulnerabilities: None"
    codebase: List[Vulnerability] = vulnerabilities.get(request.codebase, [])
    selected_vulns: Vulnerability = None
    for vuln in codebase:
        if vuln.title.strip() == request.title.strip():
            selected_vulns = vuln
            break

    if selected_vulns:
        code_data = f"## {request.codebase}\nVulnerabilities: {selected_vulns.model_dump_json(indent=4)}"

    return HumanMessage(
        content=PromptTemplate(
            input_variables=["user_feedback"],
            template="""
                Analyze the user question: "{user_feedback}"
                Read this codebase and the vulnerabilities found in it: {codebase}
            """,
        ).format(user_feedback=request.user_input, codebase=code_data)
    )
