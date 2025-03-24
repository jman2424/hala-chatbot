from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import os

app = Flask(__name__)

# Load the custom Halal Chatbot model
llm = OllamaLLM(model="halal-chatbot")

# Define prompt template
prompt = PromptTemplate(
    input_variables=["input"],
    template=""" 
You are a customer service chatbot for Tariq Halal Meat.
- Give **brief responses (1-2 sentences only)**.
- **Reply quickly** and do not generate long messages.
- If more details are needed, **ask the user if they want more info**.

Customer: {input}
Chatbot:
"""
)

# ✅ Correct way to chain prompt and LLM
chatbot = prompt | llm

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Handles incoming WhatsApp messages from Twilio."""
    
    # Debugging: Print the incoming request data
    print(f"Request Data: {request.values}")
    
    incoming_msg = request.values.get("Body", "").strip()

    if not incoming_msg:
        print("No message received.")
        return "No message received", 400  # In case no message is received

    print(f"Received message: {incoming_msg}")  # Debugging line to check incoming message

    try:
        # Generate AI response using 'invoke' method for Langchain chain
        ai_response = chatbot.invoke({"input": incoming_msg})
        print(f"AI response: {ai_response}")  # Debugging line to check AI response
        
        # ✅ These lines must be inside the try block!
        print(f"Sending message to WhatsApp: {ai_response}")
        response = MessagingResponse()
        response.message(ai_response)
        return str(response)

    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Error generating AI response", 500  # In case AI fails to generate a response


@app.route("/whatsapp/status", methods=["POST"])
def whatsapp_status_callback():
    """Handles Twilio message status updates."""
    status = request.values.get("MessageStatus", "")
    message_sid = request.values.get("MessageSid", "")

    print(f"Message SID: {message_sid}, Status: {status}")

    return "Status received", 200


@app.route("/")
def home():
    return "Hello, World!"


if __name__ == "__main__":
    # Make sure to bind to the port set in the environment variable
    port = int(os.environ.get("PORT", 10000))  # Default to 5000 if not set
    app.run(host="0.0.0.0", port=port, debug=True)
