import os
import yachtdice

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

image_link = ["https://imgur.com/S22uIPp.png", "https://imgur.com/9sfxDeL.png", "https://imgur.com/0LoX59v.png", "https://imgur.com/pTUCZr0.png", "https://imgur.com/LglELJm.png", "https://imgur.com/dpKxKHw.png"]

line_bot_api = LineBotApi(channel_access_token)
def get_user_name(id):
    global line_bot_api
    profile = line_bot_api.get_profile(id)
    return profile.display_name
def send_text_message(reply_token, text):
    global line_bot_api
    
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))
    return "OK"
def send_flex_message(reply_token, text, json):
    global line_bot_api
    line_bot_api.reply_message(reply_token, FlexSendMessage(text, json))
def send_game_info(reply_token, yacht_dice, player ,update_score = False):
    the_other_player = 2 if player == 1 else 1
    if player == 1:
        player_score = yacht_dice.player1_score
        the_other_player_score = yacht_dice.player2_score
        the_other_player_total = yacht_dice.player2_total
        the_other_player_bonus_sum = yacht_dice.player2_bonus_sum
        player_name = yacht_dice.player1_name
    elif player == 2:
        player_score = yacht_dice.player2_score
        the_other_player_score = yacht_dice.player1_score
        the_other_player_total = yacht_dice.player1_total
        the_other_player_bonus_sum = yacht_dice.player1_bonus_sum
        player_name = yacht_dice.player2_name
    if update_score:
        yacht_dice.reply_json["contents"][0]["header"]["contents"][1]["text"] = "回合 " + str(yacht_dice.turn) + " / 12"
        yacht_dice.reply_json["contents"][0]["body"]["contents"][3]["contents"][2 * the_other_player + 1]["text"] = str(the_other_player_bonus_sum) + " / 63"
        yacht_dice.reply_json["contents"][0]["body"]["contents"][5]["contents"][2 * the_other_player + 1]["text"] = str(the_other_player_total)
        yacht_dice.reply_json["contents"][1]["body"]["contents"][2 * player + 1]["contents"][1]["color"] = "#F08734"
        yacht_dice.reply_json["contents"][1]["body"]["contents"][2 * the_other_player + 1]["contents"][1]["color"] = None
        yacht_dice.reply_json["contents"][0]["body"]["contents"][1]["contents"][2 * player + 1]["color"] = "#F08734"
        yacht_dice.reply_json["contents"][0]["body"]["contents"][1]["contents"][2 * the_other_player + 1]["color"] = None
        for i in range(1, 13):
            yacht_dice.reply_json["contents"][1]["body"]["contents"][2 * the_other_player + 1]["contents"][2 * i + 1]["text"] = \
            str(the_other_player_score[i - 1]) if the_other_player_score[i - 1] != -1 else "0"

    yacht_dice.reply_json["contents"][0]["header"]["contents"][2]["text"] = "輪到玩家" + player_name +"，還有" + str(yacht_dice.rest_times) + "次"
    for i in range(1, 13):
        if player_score[i - 1] == -1:
            yacht_dice.reply_json["contents"][1]["body"]["contents"][2 * player + 1]["contents"][2 * i + 1]["text"] = \
            "(" + str(yacht_dice.calc_dice(i)) + ")"
    for i in range(0, 5):
        yacht_dice.reply_json["contents"][0]["body"]["contents"][8]["contents"][i]["url"] = \
        image_link[yacht_dice.dice_state[i] - 1]
    
    global line_bot_api
    line_bot_api.reply_message(reply_token, FlexSendMessage('game info', yacht_dice.reply_json))

"""
def send_image_url(id, img_url):
    pass

def send_button_message(id, text, buttons):
    pass
"""
