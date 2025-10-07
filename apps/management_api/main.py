from fastapi import FastAPI
from dotenv import load_dotenv
from src.agents.orchestrator import ChatOrchestrator
from src.utils.pymodels import ChatRequest, ChatResponse
from src.utils.common import PORT, logger, vulnerabilities

# -----------------------------------

load_dotenv()
app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint to check if the API is running."""
    logger.info("Root endpoint hit.")
    return {"message": "Management API is running"}


@app.get("/vulnerabilities")
def get_vulnerabilities():
    """Return all vulnerabilities parsed from the CSV file."""
    logger.info("Retrieving vulnerabilities.")
    return {
        codebase: [v.model_dump() for v in vulns]
        for codebase, vulns in vulnerabilities.items()
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Handle a chatbot interaction (frontend stores memory)."""
    orchestrator = ChatOrchestrator()
    return orchestrator.invoke(request)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint hit.")
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Management API on port %s", PORT)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
