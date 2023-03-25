from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

application = Flask(__name__)

@application.route('/')
def hello():
    return 'hello'

@application.route('/bot', methods=['POST'])
def message():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    if '1' in incoming_msg:
        resp.message('you sent a 1')
    else:
        resp.message('you did not send a 1')
    
    print(Response(str(resp), mimetype="application/xml"))
    
    return Response(str(resp), mimetype="application/xml")

if __name__ == '__main__':
    application.run(host='127.0.0.1', port=5000, debug=True)
