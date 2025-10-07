from dotenv import load_dotenv
from src.agents.orchestrator import ChatOrchestrator
from src.utils.pymodels import ChatRequest
from src.utils.common import logger


load_dotenv()

if __name__ == "__main__":
    orchestrator = ChatOrchestrator()
    request = ChatRequest(
        memory=[],
        codebase="n/a",
        title="n/a",
        user_input="The authentication logic is backwards - it's allowing access when credentials are invalid.",
    )
    response = orchestrator.invoke(request)
    logger.info("Response: %s", response.model_dump_json(indent=2))
