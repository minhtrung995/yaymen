# -*- coding: utf8 -*-
import os
import sys
import json
from datetime import datetime
from flask import Flask, request
from waitress import serve

import message_process as mp

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world! This is chatbot", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events
    data = request.get_json()    
    log(data)  # you may not want to log every incoming message in production, but it's good for testing
    mp.main_process(data)
    return "ok", 200

def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = msg.format(*args, **kwargs)
        #print u"{}: {}".format(datetime.now(), msg)
        print(msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()

if __name__ == '__main__':
    log("starting server")
    app.run(debug=True) #web: waitress-serve --port=$PORT app:app #heroku ps:scale web=1    
    #if os.environ.get('APP_LOCATION') != 'heroku':
    #    os.environ["PORT"] = '8090'
    #serve(app,host="0.0.0.0", port= os.environ.get('PORT', 8080))
