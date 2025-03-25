from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import os

app = Flask(__name__)

# ✅ Load the Halal Chatbot model
try:
    llm = OllamaLLM(model="halal-chatbot")
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
    """Handles incoming WhatsApp messages from Twilio."""
    
    try:
        print(f"🔹 Incoming Request Data: {request.values}")  # Debugging
        
        # ✅ Get the incoming message from WhatsApp
        incoming_msg = request.values.get("Body", "").strip()
        
        if not incoming_msg:
            print("⚠️ No message received.")
            return "No message received", 400  # Bad request
        
        print(f"✅ Received Message: {incoming_msg}")

        # ✅ Generate AI response
        print("🟡 Generating AI response...")
        ai_response = chatbot.invoke({"input": incoming_msg})
        
        print(f"✅ AI Response: {ai_response}")  # Log AI response
        
        # ✅ Create Twilio response
        response = MessagingResponse()
        response.message(ai_response)
        
        print("✅ Sending response back to WhatsApp")
        return str(response)

    except Exception as e:
        print(f"❌ ERROR: {e}")  # Log errors
        return f"Internal Server Error: {e}", 500  # Return error message

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
    app.run(host="0.0.0.0", port=port, debug=True)
