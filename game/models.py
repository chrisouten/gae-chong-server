from random import randint

from django.db import models

from account.models import UserProfile
from listfield import ListField

MATCH_TYPES = (
    (1,'One Game Match'),
    (2,'Best 2 out of 3'),
    (3,'Best 3 out of 5'),
)

class BoardSpace():
    EMPTY = 0
    PLAYER_1 = 1
    PLAYER_2 = 2
    PLAYER_1_BLOCKER = 3
    PLAYER_2_BLOCKER = 4

MOVE_TYPES = (
    (BoardSpace.PLAYER_1, 'Player 1 moved'),
    (BoardSpace.PLAYER_1_BLOCKER, 'Player 1 played blocker'),
    (BoardSpace.PLAYER_2, 'Player 2 moved'),
    (BoardSpace.PLAYER_2_BLOCKER, 'Player 2 played blocker')
)

class MatchManager(models.Manager):
    
    def create_match(self, chonger_1, chonger_2, match_type, public):
        match = self.create(
            chonger_1 = chonger_1,
            chonger_2 = chonger_2,
            match_type = match_type,
            public = public
        )
        match.create_game()
        return match

class Match(models.Model):
    chonger_1 = models.ForeignKey(UserProfile)
    chonger_2 = models.ForeignKey(UserProfile)
    chonger_1_wins = models.IntegerField(default=0)
    chonger_2_wins = models.IntegerField(default=0)
    match_type = models.IntegerField(choices=MATCH_TYPES)
    public = models.BooleanField(default=True)
    
    objects = MatchManager()
    
    def create_game(self):
        if self.chonger_1_wins < self.match_type or self.chonger_2_wins < self.match_type:
            Game.objects.create_game(self)
            

class GameManager(models.Manager):
    p1_start= [7,4]
    p2_start = [0,3]
    
    def create_initial_board_state(self):
        board = []
        row = []
        for x in range(0,8):
            for y in range(0,8):
                row.append(BoardSpace.EMPTY)
            board.append(row)
            row = []
        board[self.p1_start[0]][self.p1_start[1]] = BoardSpace.PLAYER_1
        board[self.p2_start[0]][self.p2_start[1]] = BoardSpace.PLAYER_2
        return board
    
    def create_game(self, match):
        board = self.create_initial_board_state()
        
        if match.games.count() > 0:
            last_game = match.games.all().order_by('-id')[0]
            p1 = last_game.player_2
            p2 = last_game.player_1
        else:
            rand = randint(0,1)
            if rand:
                p1 = match.chonger_1
                p2 = match.chonger_2
            else:
                p1 = match.chonger_2
                p2 = match.chonger_1
        game = self.create(
            match = match,
            player_1 = p1,
            player_2 = p2,
            current_turn = p1,
            board = board
        )
        return game
    
class Game(models.Model):
    match = models.ForeignKey(Match, related_name="games")
    player_1 = models.ForeignKey(UserProfile)
    player_2 = models.ForeignKey(UserProfile)
    current_turn = models.ForeignKey(UserProfile)
    player_1_blockers = models.IntegerField(default=6)
    player_2_blockers = models.IntegerField(default=7)
    winner = models.ForeignKey(UserProfile, null=True)
    board = ListField()
    
    objects = GameManager()

    def get_last_move(self):
        return self.moves.all().order_by('-move_number')[0]
    
class Move(models.Model):
    game = models.ForeignKey(Game, related_name="moves")
    player = models.ForeignKey(UserProfile)
    move_type = models.IntegerField(choices=MOVE_TYPES)
    move_number = models.IntegerField()
    move_x_pos = models.IntegerField()
    move_y_pos = models.IntegerField()
    
                
                