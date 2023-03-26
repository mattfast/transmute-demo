from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/bot', methods=['POST'])
def message():
    incoming_msg = request.values.get('Body', '').lower()
    message_number = request.values.get('To', 'Weird no number')
    value_keys = str(request.values)
    resp = MessagingResponse()
    if '1' in incoming_msg:
        resp.message('you sent a 1. good for you.')
        resp.message(value_keys)
        resp.message(message_number)
    else:
        resp.message('you did not send a 1. fuck you')
    
    print(Response(str(resp), mimetype="application/xml"))
    
    return Response(str(resp), mimetype="application/xml")

if __name__ == '__main__':
    app.debug=True
    app.run()
