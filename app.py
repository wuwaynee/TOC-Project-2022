import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
load_dotenv()
from fsm import TocMachine

from utils import *


machine = TocMachine(
    states=["new_state","init", "start", "end", "info", "ready_player1", "ready_player2","player1_first", "player2_first", "player1_second", "player2_second", "player1_third", "player2_third", "player1_to_2", "player2_to_1"],
    transitions=[
        {
            "trigger": "advance",
            "source": "start",
            "dest": "new_state",
            "conditions": "is_going_to_new_state",
        }
        ,
        {
            "trigger": "advance",
            "source": "*",
            "dest": "start",
            "conditions": "is_going_to_start",
        },
        {
            "trigger": "advance",
            "source": "start",
            "dest": "ready_player1",
            "conditions": "is_going_to_ready_player1",
        },
        {
            "trigger": "advance",
            "source": "ready_player1",
            "dest": "ready_player2",
            "conditions": "is_going_to_ready_player2",
        },
        {
            "trigger": "advance",
            "source": "ready_player2",
            "dest": "player1_first",
            "conditions": "is_going_to_player1_first",
        },
        {
            "trigger": "advance",
            "source": "player1_first",
            "dest": "player1_second",
            "conditions": "is_going_to_player1_second",
        },
        {
            "trigger": "advance",
            "source": "player1_first",
            "dest": "player1_to_2",
            "conditions": "is_going_to_player1_to_2",
        },
        {
            "trigger": "advance",
            "source": "player1_second",
            "dest": "player1_third",
            "conditions": "is_going_to_player1_third",
        },
        {
            "trigger": "advance",
            "source": "player1_second",
            "dest": "player1_to_2",
            "conditions": "is_going_to_player1_to_2",
        },
        {
            "trigger": "advance",
            "source": "player1_third",
            "dest": "player1_to_2",
            "conditions": "is_going_to_player1_to_2",
        },
        {
            "trigger": "advance",
            "source": "player1_to_2",
            "dest": "player2_first",
            "conditions": "is_going_to_player2_first",
        },
        {
            "trigger": "advance",
            "source": "player2_first",
            "dest": "player2_second",
            "conditions": "is_going_to_player2_second",
        },
        {
            "trigger": "advance",
            "source": "player2_first",
            "dest": "player2_to_1",
            "conditions": "is_going_to_player2_to_1",
        },
        {
            "trigger": "advance",
            "source": "player2_second",
            "dest": "player2_third",
            "conditions": "is_going_to_player2_third",
        },
        {
            "trigger": "advance",
            "source": "player2_second",
            "dest": "player2_to_1",
            "conditions": "is_going_to_player2_to_1",
        },
        {
            "trigger": "advance",
            "source": "player2_third",
            "dest": "player2_to_1",
            "conditions": "is_going_to_player2_to_1",
        },
        {
            "trigger": "advance",
            "source": "player2_to_1",
            "dest": "end",
            "conditions": "is_going_to_end",
        },
        {
            "trigger": "advance",
            "source": "player2_to_1",
            "dest": "player1_first",
            "conditions": "is_going_to_player1_first",
        },
        {
            "trigger": "advance",
            "source": "init",
            "dest": "info",
            "conditions": "is_going_to_info",
        },
        {"trigger": "go_init", "source": ["end", "info"], "dest": "init"},
    ],
    initial="init",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")
    

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        #print(f"REQUEST BODY: \n{body}")

        machine.advance(event)
    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
    
