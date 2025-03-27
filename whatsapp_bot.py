from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import os
import traceback

app = Flask(__name__)

# ✅ Load the Halal Chatbot model
try:
  llm = OllamaLLM(model="halal-chatbot", base_url="https://4c92-2a02-6b67-d904-ef00-f0eb-8.ngrok.io")
  print("✅ Halal Chatbot model loaded successfully.")
except Exception as e:
    print(f"❌ ERROR: Failed to load model: {e}")

# ✅ Define chatbot prompt template
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

# ✅ Connect prompt with Langchain model
chatbot = prompt | llm

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    try:
        print(f"Request Data: {request.values}")  # Debugging

        incoming_msg = request.values.get("Body", "").strip()

        if not incoming_msg:
            print("No message received.")
            return "No message received", 400

        print(f"Received message: {incoming_msg}")  # Debugging

        # Generate AI response
        ai_response = chatbot.invoke({"input": incoming_msg})
        print(f"AI response: {ai_response}")  # Debugging

        response = MessagingResponse()
        response.message(ai_response)
        return str(response)

    except Exception as e:
        print("Error in /whatsapp route:")
        traceback.print_exc()  # Print full error traceback
        return "Error generating AI response", 500

    

@app.route("/whatsapp/status", methods=["POST"])
def whatsapp_status_callback():
    """Handles Twilio message status updates."""
    status = request.values.get("MessageStatus", "")
    message_sid = request.values.get("MessageSid", "")

    print(f"🔹 Message SID: {message_sid}, Status: {status}")
    return "Status received", 200

@app.route("/")
def home():
    return "✅ Hello, Render! Your chatbot is running."

if __name__ == "__main__":
    # ✅ Fix: Use dynamic PORT for Render
    port = int(os.environ.get("PORT", 10000))  
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
