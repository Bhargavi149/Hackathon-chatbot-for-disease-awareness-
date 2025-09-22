import os
from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from googletrans import Translator
from groq import Client
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

groq_api_key = os.environ.get("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")
if not groq_api_key:
    raise ValueError("⚠️ Missing GROQ_API_KEY in .env")

# Initialize Groq client
groq_client = Client(api_key=groq_api_key)

# Initialize translator
translator = Translator()

# -------------------------------
# Chatbot logic
# -------------------------------
def chatbot_response(user_input: str) -> str:
    try:
        # Detect user language
        detected = translator.detect(user_input)
        user_lang = detected.lang

        # Translate input → English
        input_en = user_input
        if user_lang != "en":
            input_en = translator.translate(user_input, src=user_lang, dest="en").text

        # Call Groq LLM
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": input_en}],
            model="llama3-8b-8192"
        )

        reply_en = response.choices[0].message["content"].strip()

        # Translate reply → user language
        if user_lang != "en":
            reply_final = translator.translate(reply_en, src="en", dest=user_lang).text
        else:
            reply_final = reply_en

        return reply_final

    except Exception as e:
        print(f"❌ Error: {e}")
        return "⚠️ Sorry, something went wrong."

# -------------------------------
# FastAPI setup
# -------------------------------
app = FastAPI()

@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(Body: str = Form(...)):
    bot_reply = chatbot_response(Body)
    twiml = MessagingResponse()
    twiml.message(bot_reply)
    return str(twiml)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Health Chatbot (Multilingual)"}
