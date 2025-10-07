import os
import uuid
import logging
from typing import Dict, List, Annotated
import pandas as pd
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from src.utils.pymodels import Vulnerability
from src.utils.pymodels import ChatResponse, ChatRequest

# ---------- All util Functions ----------


class ChatOrchestratorState(TypedDict):
    """Represents the state of the chat orchestrator."""

    messages: Annotated[list[BaseMessage], add_messages]


def fetch_csv_data(
    file_path: str = "src/utils/data.csv",
) -> Dict[str, List[Vulnerability]]:
    """Fetch data from a CSV file and map codebases to lists of Pydantic models."""
    try:
        df = pd.read_csv(file_path)
        df = df.fillna("n/a")
        data: Dict[str, List[Vulnerability]] = {}

        for record in df.to_dict(orient="records"):
            title_value = str(record.get("Title", "")).strip()
            if not title_value:
                title_value = str(uuid.uuid4())

            vuln = Vulnerability(
                code=record["Vulnerable"],
                title=title_value,
                category=record["Category"],
                fix_code=record["Fixed"],
                notes=record["Notes"],
            )
            data.setdefault(record["Codebase"], []).append(vuln)

        return data

    except Exception as e:
        logging.error("Error reading CSV file at %s: %s", file_path, e)
        raise


def load_system_message(dir_path: str = "src/agent_prompt/prompts") -> dict[str, str]:
    """Load system messages from markdown files in the specified directory."""
    messages = {}

    for file_name in os.listdir(dir_path):
        if file_name.endswith(".md"):
            file_path = os.path.join(dir_path, file_name)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                messages[os.path.splitext(file_name)[0]] = content

    return messages


def make_orch_output(
    reply: ChatOrchestratorState, request: ChatRequest
) -> ChatResponse:
    """Format the orchestrator output."""
    invalid = {None, "", "n/a"}
    if request.codebase in invalid or request.title in invalid:
        response = f"### Predicted Class: \n{reply['messages'][-1].content}"
    else:
        response = f"### Predicted Class: \n{reply['messages'][-2].content}\n\n{reply['messages'][-1].content}"
    return ChatResponse(response=response)


# ---------- Global Variables ----------


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
PORT: int = int(os.getenv("PORT", "5000"))
SYS_PROMPTS: Dict[str, str] = load_system_message()
vulnerabilities: Dict[str, List[Vulnerability]] = fetch_csv_data()
