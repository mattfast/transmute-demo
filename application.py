import os
from threading import Thread
from typing import Optional

import pinecone
from flask import Flask, Response, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from constants import (
    DEFAULT_PERSONA,
    SUMMARY_TABLE_MAIN_SUMMARY,
    SUMMARY_TABLE_SYNTHESIS,
    USER_TABLE_PERSONA,
    USER_TABLE_PINECONE_INDEX,
    MessageType,
)
from db.api import (
    add_friend_info,
    create_new_user,
    update_user_index,
    fetch_link_info,
    fetch_user_info,
    insert_summary_info,
    update_persona_info,
)
from db.embeddings import create_new_user_index
from helpers import format_summaries_for_text, process_new_link

# Stop hardcoding this 
pinecone.init(api_key="b40966ec-276b-47ca-8cde-c1580abd5f67", environment="us-east4-gcp")

app = Flask(__name__)

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)


def generate_reponse(user_number, incoming_msg):
    user_info = fetch_user_info(user_number)
    is_first_time = False
    if user_info is None:
        client.messages.create(
            body="Welcome to Transmute! We find all the new and relevant information from the links you send us and connect them to the links you've sent us in the past. Please hold tight while we set up your environment. This could take a couple minutes.",
            from_=os.environ["TWILIO_PRIMARY_NUMBER"],
            to=user_number,
        )
        is_first_time = True
        index_name = create_new_user_index()
        create_new_user(user_number, index_name)
        index = pinecone.Index(index_name)
        persona = DEFAULT_PERSONA
    elif user_info[USER_TABLE_PINECONE_INDEX] is None:
        client.messages.create(
            body="Welcome to Transmute! We're making some upgrades to your environment. Please hold tight while we make these changes. This could take a couple minutes.",
            from_=os.environ["TWILIO_PRIMARY_NUMBER"],
            to=user_number,
        )

        index_name = create_new_user_index()
        update_user_index(user_number, index_name)
        index = pinecone.Index(index_name)
        persona = user_info[USER_TABLE_PERSONA]
    else:
        persona = user_info[USER_TABLE_PERSONA]
        client.messages.create(
            body=f"Welcome back to Transmute! You'll get a text in a few minutes with the insights from this link. You're current personality is: {persona}.",
            from_=os.environ["TWILIO_PRIMARY_NUMBER"],
            to=user_number,
        )
        index = pinecone.Index(user_info[USER_TABLE_PINECONE_INDEX])

    # Assume link is the incoming message
    summaries = fetch_link_info(user_number, incoming_msg)
    if summaries is not None:
        client.messages.create(
            body="Looks like you've already seen this link before",
            from_=os.environ["TWILIO_PRIMARY_NUMBER"],
            to=user_number,
        )

        formatted_resp = format_summaries_for_text(
            summaries[SUMMARY_TABLE_MAIN_SUMMARY], summaries[SUMMARY_TABLE_SYNTHESIS]
        )
    else:
        summary, synthesis, sources = process_new_link(incoming_msg, persona, index)

        if summary == synthesis == sources == "":
            client.messages.create(
                body="Something went wrong. Please send us a different link.",
                from_=os.environ["TWILIO_PRIMARY_NUMBER"],
                to=user_number,
            )
            return

        insert_summary_info(user_number, incoming_msg, summary, synthesis)
        synthesis_reason = ""
        if is_first_time:
            synthesis_reason = " since this is your first time using Transmute."
        formatted_resp = format_summaries_for_text(summary, synthesis, sources, synthesis_reason=synthesis_reason)

    for res in formatted_resp:
        client.messages.create(
            body=res, from_=os.environ["TWILIO_PRIMARY_NUMBER"], to=user_number
        )

    client.messages.create(
        body="Send us another link, text \"info\" for more commands, or visit https://gptwitter-neon.vercel.app/"
             " for your full digest.",
        from_=os.environ["TWILIO_PRIMARY_NUMBER"],
        to=user_number,
    )


def determine_message_type(incoming_msg: str) -> MessageType:
    lowered = incoming_msg.lower()
    if lowered == "info":
        return MessageType.INFO_MESSAGE
    if lowered.startswith("as"):
        return MessageType.PERSONA_MESSAGE
    elif lowered.startswith("add friend"):
        return MessageType.ADD_FRIEND_MESSAGE
    elif lowered.startswith("call me"):
        return MessageType.ADD_NAME_MESSAGE
    return MessageType.INSIGHTS_MESSAGE


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

    message_type = determine_message_type(incoming_msg)
    if message_type is MessageType.INFO_MESSAGE:
        resp.message("Send a link to us to learn more or change you're personality by texting \"as a personality\" (eg. as a curious child)")
    elif message_type is MessageType.PERSONA_MESSAGE:
        return process_persona_message(incoming_msg, user_number)
    elif message_type is MessageType.ADD_FRIEND_MESSAGE:
        return process_friend_message(incoming_msg, user_number)
    elif message_type is MessageType.INSIGHTS_MESSAGE:
        t = Thread(target=generate_reponse, args=(user_number, incoming_msg))
        t.start()
    else:
        resp.message(f"Could not process message {incoming_msg}. Please try again.")

    return Response(str(resp), mimetype="application/xml")


def process_msg_number(msg_num: str) -> Optional[str]:
    """Process message number into a proper format."""
    number_prefix = "+1"
    if len(msg_num) == 10:
        return number_prefix + msg_num
    elif len(msg_num) == 11:
        return "+" + msg_num
    elif len(msg_num) == 12:
        return msg_num
    return None


def process_friend_message(incoming_msg: str, user_number: str) -> Response:
    """Process add friend message.

    Format: add friend number: ###
    """
    resp = MessagingResponse()
    number_list = incoming_msg.split(":")
    if len(number_list) == 1:
        resp.message(
            'Incorrect format for adding a friend, please text "add friend number: #"'
        )
        return Response(str(resp), mimetype="application/xml")
    msg_num = number_list[-1].strip()
    processed_num = process_msg_number(msg_num)

    if processed_num is None:
        resp.message(
            f'Number provided: {msg_num} is incorrect. Please retry by texting "add friend number: #"'
        )
    else:
        add_friend_info(user_number, processed_num)
        resp.message("Succesfully added friend's number!")

    return Response(str(resp), mimetype="application/xml")


def process_persona_message(incoming_msg: str, user_number: str) -> Response:
    """Process persona update message.

    Format: as a "persona"
    """
    persona_list = incoming_msg[2:].split()
    resp = MessagingResponse()

    # Update persona
    if len(persona_list) > 0:
        article = persona_list[0]
        if "a" or "an" in article:
            persona_list = persona_list[1:]
        persona = " ".join(persona_list)
        update_persona_info(user_number, persona)
        resp.message(
            "Changed your personality! Send us a link to learn more and deepen your connections."
        )
        return Response(str(resp), mimetype="application/xml")


if __name__ == "__main__":
    app.debug = True
    app.run()
