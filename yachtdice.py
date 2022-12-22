import json

from random import randint

class YachtDice():
    def __init__(self):
        self.dice_state = [0, 0, 0, 0, 0]
        self.player1_score = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        self.player1_total = 0
        self.player1_bonus_sum = 0
        self.player1_name = "A"
        self.player1_id = "0"
        self.player2_score = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        self.player2_total = 0
        self.player2_bonus_sum = 0
        self.player2_name = "B"
        self.player2_id = "0"
        self.turn = 1
        self.rest_times = 0
        self.reply_json = json.load(open('reply.json', encoding='utf-8'))
    def change_name(self):
        self.reply_json["contents"][1]["body"]["contents"][3]["contents"][1]["text"] = self.player1_name
        self.reply_json["contents"][1]["body"]["contents"][5]["contents"][1]["text"] = self.player2_name
        self.reply_json["contents"][0]["body"]["contents"][1]["contents"][3]["text"] = self.player1_name
        self.reply_json["contents"][0]["body"]["contents"][1]["contents"][5]["text"] = self.player2_name
    def roll_dice(self):
        for i in range(0, 5):
            self.dice_state[i] = randint(1, 6)
    def select_and_roll_dice(self, selection):
        for i in range(0, 5) :
            if str(i + 1) in selection:
                self.dice_state[i] = randint(1, 6)
    def calc_dice(self, dice_type):
        if not self.check_dice(dice_type):
            return 0
        if dice_type < 7:
            return self.dice_state.count(dice_type) * dice_type
        elif dice_type <= 9:
            return sum(self.dice_state)
        elif dice_type == 10:
            return 15
        elif dice_type == 11:
            return 30
        elif dice_type == 12:
            return 50
        
    def check_dice(self, dice_type):
        count = [0, 0, 0, 0, 0, 0]
        for i in range(1, 7):
            count[self.dice_state.count(i)] += 1
        if dice_type <= 7:
            return True
        elif dice_type == 8:
            return count[3] == 1 and count[2] == 1
        elif dice_type == 9:
            return count[4] == 1 and count[1] == 1
        elif dice_type == 10:
            return (count[1] == 5 and self.dice_state.count(3) and self.dice_state.count(4)) \
            or (count[1] == 3 and self.dice_state.count(3) and self.dice_state.count(4) and \
                ((self.dice_state.count(1) and self.dice_state.count(2)) or (self.dice_state.count(2) and self.dice_state.count(5)) or (self.dice_state.count(5) and self.dice_state.count(6))))
        elif dice_type == 11:
            return count[1] == 5 and self.dice_state.count(1) != self.dice_state.count(6)
        elif dice_type == 12:
            return count[5] == 1
        else:
            return False
    def update_score(self, player, score, dice_type):
        if player == 1:
            self.player1_score[dice_type - 1] = score
            if dice_type <= 6:
                self.player1_bonus_sum += score
                if self.player1_bonus_sum >= 63:
                    self.player1_total += 35
            self.player1_total += score
        elif player == 2:
            self.player2_score[dice_type - 1] = score
            if dice_type <= 6:
                self.player2_bonus_sum += score
                if self.player2_bonus_sum >= 63:
                    self.player2_total += 35
            self.player2_total += score