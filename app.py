import os
from flask import Flask, request
from twilio.rest import Client
import threading

# Import your modules
import database
import ai_agent
import payments

GEMINI_KEY = "YOUR_GEMINI_KEY"
TWILIO_SID = "YOUR_TWILIO_SID"
TWILIO_TOKEN = "YOUR_TWILIO_TOKEN"
TWILIO_NUMBER = "YOUR_TWILIO_NUMBER"
NGROK_AUTH_TOKEN = "YOUR_NGROK_TOKEN"
os.environ["GEMINI_KEY"] = GEMINI_KEY 

app = Flask(__name__)
client = Client(TWILIO_SID, TWILIO_TOKEN)
database.init_db()

def send_whatsapp_message(to_number, body_text):
    max_length = 1500
    for i in range(0, len(body_text), max_length):
        chunk = body_text[i:i+max_length]
        try:
            client.messages.create(from_=f"whatsapp:{TWILIO_NUMBER}", body=chunk, to=to_number)
        except Exception as e:
            print(f"Error: {e}")

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip()
    sender_number = request.values.get("From", "")
    
    # Logic
    database.add_user(sender_number)
    menu_context = database.get_menu_string()
    decision = ai_agent.get_ai_decision(incoming_msg, menu_context)
    
    intent = decision.get("intent", "chat")
    response_text = decision.get("response_text", "")
    final_response = response_text

    if intent == "menu":
        final_response += "\n\n" + menu_context
    elif intent == "order":
        order_items = decision.get("order_items", [])
        if order_items:
            total_price = sum([item['price'] * item.get('qty', 1) for item in order_items])
            pay_link, pay_id = payments.generate_payment_link(total_price)
            item_details = ", ".join([f"{i.get('qty',1)}x {i['item_name']}" for i in order_items])
            database.add_order(sender_number, item_details, total_price, pay_id)
            final_response += f"\n\n💰 Total: ₹{total_price}\n💳 Pay: {pay_link}"

    send_whatsapp_message(sender_number, final_response)
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000, use_reloader=False)