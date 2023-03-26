from flask import Flask, request, Response
import pinecone
from twilio.twiml.messaging_response import MessagingResponse
from db.api import fetch_user_info, create_new_user
from db.embeddings import create_new_user_index
from constants import USER_TABLE_PINECONE_INDEX

# Stop hardcoding this
pinecone.init(api_key="7348774e-f6d1-47f6-91c2-b955e910fe4c",
              environment="us-east1-gcp")

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/bot', methods=['POST'])
def message():
    incoming_msg = request.values.get('Body', '').lower()
    user_number = request.values.get('From', '')
    resp = MessagingResponse()

    if len(user_number) == 0:
        resp.message("Sorry, we couldn't properly identify your information. "
                     "Please try texting this number from another phone.")
        return Response(str(resp), mimetype="application/xml")

    user_info = fetch_user_info(user_number)
    if user_info is None:
        # index_name = create_new_user_index()
        index_name = "new-user"
        create_new_user(user_number, index_name)
        index = pinecone.Index(index_name)
    else:
        index = user_info[USER_TABLE_PINECONE_INDEX]

    if '1' in incoming_msg:
        resp.message('you sent a 1. good for you.')
        resp.message("Created a new user")
        resp.message(user_number)
        resp.message(f"Pinecone Index: {index}")
    else:
        resp.message('you did not send a 1. fuck you')
    
    print(Response(str(resp), mimetype="application/xml"))
    
    return Response(str(resp), mimetype="application/xml")

if __name__ == '__main__':
    app.debug=True
    app.run()
