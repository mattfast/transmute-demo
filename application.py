from threading import Thread
import os

import pinecone
from flask import Flask, Response, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

from constants import (
    DEFAULT_PERSONA,
    SUMMARY_TABLE_MAIN_SUMMARY,
    SUMMARY_TABLE_SYNTHESIS,
    USER_TABLE_PERSONA,
    USER_TABLE_PINECONE_INDEX,
)
from db.api import create_new_user, fetch_link_info, fetch_user_info
from db.embeddings import create_new_user_index
from helpers import format_summaries_for_text, process_new_link

# Stop hardcoding this
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"], environment="us-east1-gcp"
)

app = Flask(__name__)

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

@app.route("/")
def hello_world():
    return "Hello, World!"

def generate_reponse(user_number, incoming_msg):
    resp = ""

    user_info = fetch_user_info(user_number)
    if user_info is None:
        # index_name = create_new_user_index()
        index_name = "new-user"
        create_new_user(user_number, index_name)
        index = pinecone.Index(index_name)
        persona = DEFAULT_PERSONA
    else:
        index = pinecone.Index(user_info[USER_TABLE_PINECONE_INDEX])
        persona = user_info[USER_TABLE_PERSONA]

    # Assume link is the incoming message
    summaries = fetch_link_info(user_number, incoming_msg)
    if summaries is not None:
        resp += "You've already sent this link before! Here's the summary."
        formatted_resp = format_summaries_for_text(
            summaries[SUMMARY_TABLE_MAIN_SUMMARY], summaries[SUMMARY_TABLE_SYNTHESIS]
        )
    else:
        summary, synthesis = process_new_link(incoming_msg, persona, index)
        formatted_resp = format_summaries_for_text(summary, synthesis)

    for res in formatted_resp:
        resp += res

    client.messages.create(
        body=res,
        from_=os.environ["TWILIO_PRIMARY_NUMBER"],
        to=user_number
    )


@app.route("/bot", methods=["POST"])
def message():
    incoming_msg = request.values.get("Body", "").lower()
    user_number = request.values.get("From", "")
    resp = MessagingResponse()

    if len(user_number) == 0:
        resp.message(
            "Sorry, we couldn't properly identify your information. "
            "Please try texting this number from another phone."
        )
        return Response(str(resp), mimetype="application/xml")
    
    t = Thread(target=generate_reponse, args=(user_number,incoming_msg))
    t.start()

    resp.message("Generating interesting insights for this webpage! Hold tight.")
    return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    app.debug = True
    app.run()
