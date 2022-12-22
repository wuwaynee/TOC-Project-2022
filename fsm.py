from transitions.extensions import GraphMachine

from utils import *
from yachtdice import *

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.start_reply = json.load(open('start.json', encoding="utf-8"))
    def is_going_to_info(self, event):
        text = event.message.text
        return text.lower() == "?"
    def is_going_to_new_state(self, event):
        text = event.message.text
        return text.lower() == "new"
    def is_going_to_start(self, event):
        text = event.message.text
        return text.lower() == "start"
    def is_going_to_ready_player1(self, event):
        text = event.message.text
        return text.lower() == "+"
    def is_going_to_ready_player2(self, event):
        text = event.message.text
        return text.lower() == "+"      
    def is_going_to_player1_first(self, event):
        return self.yacht_dice.turn != 13

    def is_going_to_player1_second(self, event):
        text = event.message.text
        reply_token = event.reply_token
        if text[:4] != "roll":
            return False
        elif  event.source.user_id != self.yacht_dice.player1_id:
            send_text_message(reply_token, "現在是另一位玩家的回合")
            return False
        else:
            return True

    def is_going_to_player1_third(self, event):
        text = event.message.text
        reply_token = event.reply_token
        if text[:4] != "roll":
            return False
        elif  event.source.user_id != self.yacht_dice.player1_id:
            send_text_message(reply_token, "現在是另一位玩家的回合")
            return False
        else:
            return True

    def is_going_to_player1_to_2(self, event):
        text = event.message.text
        reply_token = event.reply_token
        if text[:6] != "select":
            return False
        elif int(text[7:]) > 12 or int(text[7:]) < 1:
            send_text_message(reply_token, "編號請在 1 ~ 12")
            return False
        elif self.yacht_dice.player1_score[int(text[7:]) - 1] != -1:
            send_text_message(reply_token, "不能重複選擇")
            return False
        elif  event.source.user_id != self.yacht_dice.player1_id:
            send_text_message(reply_token, "現在是另一位玩家的回合")
            return False
        else:
            return True
    def is_going_to_player2_first(self, event):
        text = event.message.text
        return True

    def is_going_to_player2_second(self, event):
        text = event.message.text
        reply_token = event.reply_token
        if text[:4] != "roll":
            return False
        elif  event.source.user_id != self.yacht_dice.player2_id:
            send_text_message(reply_token, "現在是另一位玩家的回合")
            return False
        else:
            return True

    def is_going_to_player2_third(self, event):
        text = event.message.text
        reply_token = event.reply_token
        if text[:4] != "roll":
            return False
        elif  event.source.user_id != self.yacht_dice.player2_id:
            send_text_message(reply_token, "現在是另一位玩家的回合")
            return False
        else:
            return True
    def is_going_to_end(self, event):
        return self.yacht_dice.turn == 13

    def is_going_to_player2_to_1(self, event):
        text = event.message.text
        reply_token = event.reply_token
        if text[:6] != "select":
            return False
        elif int(text[7:]) > 12 or int(text[7:]) < 1:
            send_text_message(reply_token, "編號請在 1 ~ 12")
            return False
        elif self.yacht_dice.player2_score[int(text[7:]) - 1] != -1:
            send_text_message(reply_token, "不能重複選擇")
            return False
        elif  event.source.user_id != self.yacht_dice.player2_id:
            send_text_message(reply_token, "現在是另一位玩家的回合")
            return False
        else:
            return True

    def on_enter_ready_player1(self, event):
        self.yacht_dice.player1_id = event.source.user_id
        self.yacht_dice.player1_name = get_user_name(event.source.user_id)
    def on_enter_ready_player2(self, event):
        self.yacht_dice.player2_id = event.source.user_id
        self.yacht_dice.player2_name = get_user_name(event.source.user_id)
        self.yacht_dice.change_name()
        self.advance(event)

    def on_enter_start(self, event):
        self.yacht_dice = YachtDice()
        reply_token = event.reply_token
        send_flex_message(reply_token, "start info", self.start_reply)
    def on_enter_end(self, event):
        reply_token = event.reply_token
        if self.yacht_dice.player1_total == self.yacht_dice.player2_total:
            send_text_message(reply_token, "恭喜平手")
        else:
            winner_name = self.yacht_dice.player1_name if self.yacht_dice.player1_total > self.yacht_dice.player2_total else self.yacht_dice.player2_name
            winner_score = self.yacht_dice.player1_total if self.yacht_dice.player1_total > self.yacht_dice.player2_total else self.yacht_dice.player2_total
            send_text_message(reply_token, "恭喜" + winner_name + "獲勝，得分為" + str(winner_score))
        self.go_init()

    def on_enter_info(self, event):
        reply_token = event.reply_token
        send_text_message(reply_token, "Info")
        self.go_init()

    def on_enter_player1_first(self, event):
        self.yacht_dice.roll_dice()
        self.yacht_dice.rest_times = 2
        reply_token = event.reply_token
        send_game_info(reply_token, self.yacht_dice, 1, update_score=True)

    def on_enter_player1_second(self, event):
        self.yacht_dice.select_and_roll_dice(event.message.text[4:])
        self.yacht_dice.rest_times -= 1
        reply_token = event.reply_token
        send_game_info(reply_token, self.yacht_dice, 1)
    def on_enter_player1_third(self, event):
        self.yacht_dice.select_and_roll_dice(event.message.text[4:])
        self.yacht_dice.rest_times -= 1
        reply_token = event.reply_token
        send_game_info(reply_token, self.yacht_dice, 1)

    def on_enter_player1_to_2(self, event):
        dice_type = int(event.message.text[7:])
        score = self.yacht_dice.calc_dice(dice_type)
        self.yacht_dice.update_score(1, score, dice_type)
        self.advance(event)

    def on_enter_player2_first(self, event):
        self.yacht_dice.roll_dice()
        self.yacht_dice.rest_times = 2
        reply_token = event.reply_token
        send_game_info(reply_token, self.yacht_dice, 2, update_score=True)
        

    def on_enter_player2_second(self, event):
        self.yacht_dice.select_and_roll_dice(event.message.text[4:])
        self.yacht_dice.rest_times -= 1
        reply_token = event.reply_token
        send_game_info(reply_token, self.yacht_dice, 2)
    def on_enter_player2_third(self, event):
        self.yacht_dice.select_and_roll_dice(event.message.text[4:])
        self.yacht_dice.rest_times -= 1
        reply_token = event.reply_token
        send_game_info(reply_token, self.yacht_dice, 2)

    def on_enter_player2_to_1(self, event):
        dice_type = int(event.message.text[7:])
        score = self.yacht_dice.calc_dice(dice_type)
        self.yacht_dice.update_score(2, score, dice_type)
        self.yacht_dice.turn += 1
        self.advance(event)