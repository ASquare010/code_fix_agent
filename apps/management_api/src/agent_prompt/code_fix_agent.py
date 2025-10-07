from typing import List
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from src.utils.pymodels import ChatRequest, Vulnerability
from src.utils.common import SYS_PROMPTS
from src.utils.common import vulnerabilities


def get_fix_user_prompt(class_category: str, request: ChatRequest) -> HumanMessage:
    """Create a user prompt message."""

    code_data = "## No codebase provided.\nVulnerabilities: None"
    codebase: List[Vulnerability] = vulnerabilities.get(request.codebase, [])
    selected_vulns: Vulnerability = None
    for vuln in codebase:
        if vuln.title.strip() == request.title.strip():
            selected_vulns = vuln
            break

    user_input = f"""
        The user has selected the category '{class_category}'.
        Please provide a code fix based on this category and the user's original input: '{request.user_input}'.
    """
    if selected_vulns:
        code_data = f"Category {request.codebase}\nVulnerabilities: {selected_vulns.model_dump_json(indent=4)}"

    return HumanMessage(
        content=PromptTemplate(
            input_variables=["user_input", "code_data"],
            template=SYS_PROMPTS["fix_agent"],
        ).format(user_input=user_input, code_data=code_data)
    )
