import requests
import gradio as gr
from src.utils.common import API_URL, PORT, logger, get_vulnerabilities
from src.utils.pymodels import ChatMessage, ChatRequest, ChatResponse, Sender


vulnerabilities = get_vulnerabilities()


# -------------------------------
# Helper functions
# -------------------------------
def chat_with_bot(
    user_message: str, history: list, selected_codebase: str, vuln_title: str
):
    """Send user message + memory to backend and return updated chat."""

    # Convert Gradio chat history into ChatMessage list
    memory = []
    for user_msg, bot_msg in history:
        if user_msg:
            memory.append(ChatMessage(sender=Sender.USER, message=user_msg))
        if bot_msg:
            memory.append(ChatMessage(sender=Sender.ASSISTANT, message=bot_msg))

    request = ChatRequest(
        memory=memory,
        user_input=user_message,
        codebase=selected_codebase,
        title=vuln_title,
    )

    r = requests.post(f"{API_URL}/chat", json=request.model_dump(), timeout=60)
    response = ChatResponse(**r.json())

    history.append((user_message, response.response))
    return history, ""


def update_titles(selected_codebase: str):
    """
    Return updated Dropdown component with vulnerability titles for the given codebase.
    """
    if not selected_codebase or selected_codebase not in vulnerabilities:
        return gr.update(choices=[], value=None)

    titles = [v.title for v in vulnerabilities[selected_codebase]]
    return gr.update(choices=titles, value=titles[0] if titles else None)


# -------------------------------
# Gradio App
# -------------------------------


def gradio_app():
    """Create the Gradio chatbot interface with two dependent dropdowns."""
    codebases = list(vulnerabilities.keys())

    if codebases:
        init_update = update_titles(codebases[0])
        initial_choices = init_update["choices"]
        initial_value = init_update["value"]
    else:
        initial_choices, initial_value = [], None

    with gr.Blocks() as gr_app:
        gr.Markdown("# 🔒 Vulnerability Chatbot")

        codebase_dropdown = gr.Dropdown(
            choices=codebases,
            label="Select Codebase",
            value=codebases[0] if codebases else None,
        )
        vuln_title_dropdown = gr.Dropdown(
            choices=initial_choices,
            value=initial_value,
            label="Select Vulnerability Title",
        )

        chatbot = gr.Chatbot(label="Conversation", height=500)
        msg = gr.Textbox(label="Your message")
        send = gr.Button("Send")

        # When codebase changes, update vulnerability titles
        codebase_dropdown.change(
            fn=update_titles, inputs=[codebase_dropdown], outputs=[vuln_title_dropdown]
        )

        # Send message with both dropdown selections
        send.click(
            fn=chat_with_bot,
            inputs=[msg, chatbot, codebase_dropdown, vuln_title_dropdown],
            outputs=[chatbot, msg],
        )
    return gr_app


if __name__ == "__main__":
    app = gradio_app()
    logger.info("Starting Gradio app on port %s", PORT)
    app.launch(server_name="0.0.0.0", server_port=PORT)
