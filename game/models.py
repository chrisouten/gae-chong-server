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

MOVE_DIRS = [
    [0,1],
    [1,0],
    [0,-1],
    [-1,0]
]

JUMP_DIRS = [
    [0,1],
    [1,0],
    [0,-1],
    [-1,0],
    [1,1],
    [-1,1],
    [-1,-1],
    [1,-1]
]

class MatchManager(models.Manager):
    
    def create_match(self, chonger_1, chonger_2, match_type, public, ranked):
        chonger_1 = UserProfile.objects.get(id=chonger_1)
        if chonger_2 is None:
            #Lets try and find an existing match
            matches = Match.objects.filter(match_type=match_type, public=public, ranked=ranked, chonger_2=None).exclude(chonger_1=chonger_1)
            if matches:
                match = matches[0]
                match.chonger_2 = chonger_1
                match.save()
                match.create_game()
                return match
        else:
            chonger_2 = UserProfile.objects.get(id=chonger_2)
        
        match = self.create(
            chonger_1 = chonger_1,
            chonger_2 = chonger_2,
            match_type = match_type,
            public = public,
            ranked = ranked
        )
        if chonger_2:
            match.create_game()
        return match

class Match(models.Model):
    chonger_1 = models.ForeignKey(UserProfile, related_name='chonger_1')
    chonger_2 = models.ForeignKey(UserProfile, null=True, related_name='chonger_2')
    chonger_1_wins = models.IntegerField(default=0)
    chonger_2_wins = models.IntegerField(default=0)
    match_type = models.IntegerField(choices=MATCH_TYPES)
    match_winner = models.ForeignKey(UserProfile, null=True, related_name='match_winner')
    public = models.BooleanField(default=True)
    ranked = models.BooleanField(default=True)
    
    objects = MatchManager()
    
    def create_game(self):
        if self.chonger_1_wins < self.match_type and self.chonger_2_wins < self.match_type:
            Game.objects.create_game(self)
        else:
            if self.chonger_1_wins == self.match_type:
                self.match_winner = self.chonger_1
            else:
                self.match_winner = self.chonger_2
            self.save()

    def json(self):
        match = {}
        match['chonger_1'] = self.chonger_1.json()
        if self.chonger_2:
            match['chonger_2'] = self.chonger_2.json()
        else:
            match['chonger_2'] = None
        match['chonger_1_wins'] = self.chonger_1_wins
        match['chonger_2_wins'] = self.chonger_2_wins
        match['match_type'] = self.match_type
        match['match_winner'] = self.match_winner
        match['public'] = self.public
        return match

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
    player_1 = models.ForeignKey(UserProfile, related_name='player_1')
    player_2 = models.ForeignKey(UserProfile, related_name='player_2')
    current_turn = models.ForeignKey(UserProfile, related_name='current_turn')
    player_1_blockers = models.IntegerField(default=6)
    player_2_blockers = models.IntegerField(default=7)
    winner = models.ForeignKey(UserProfile, null=True, related_name='winner')
    board = ListField()
    
    objects = GameManager()
    
    def get_last_move(self):
        return self.moves.all().order_by('-move_number')[0]
        
    def make_move(self, user_token, move_info):
        if not all(k in ['move_type','move_position'] for k in move_info.keys()):
            return {'error': 'Not all move data was submitted'}
        submitting_user = UserProfile.objects.get_user(user_token)
        pos = move_info['move_position']
        if pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7:
            return {'error': 'Not a valid move position'}
        if submitting_user != self.current_turn:
            return {'error': 'It is not your turn'}
        if move_info['move_type'] in [BoardSpace.PLAYER_1_BLOCKER, BoardSpace.PLAYER_2_BLOCKER]:
            if self.board[pos[0]][pos[1]] != BoardSpace.EMPTY:
                return {'error': 'Invalid Block Placement'}
            if (self.player_1 == submitting_user and self.player_1_blockers == 0) \
                or (self.player_2 == submitting_user and self.player_2_blockers == 0):
                return {'error' : 'Not enough blockers to make this move'}
            self.board[pos[0]][pos[1]] = move_info['move_type']
            if move_info['move_type'] == BoardSpace.PLAYER_1_BLOCKER:
                self.player_1_blockers = self.player_1_blockers - 1
            else:
                self.player_2_blockers = self.player_2_blockers - 1
            Move.objects.create_move(self, submitting_user, move_info)
            self.save()
                
        if move_info['move_type'] in [BoardSpace.PLAYER_1, BoardSpace.PLAYER_2]:
            vm = self.get_valid_moves()
            if pos not in vm:
                return {'error': 'Not a valid move position for your pawn'}
            self.board[pos[0]][pos[1]] = move_info['move_type']
            Move.objects.create_move(self, submitting_user, move_info)
            self.save()
        
        if self.current_turn == self.player_1:
            self.current_turn = self.player_2
        else:
            self.current_turn = self.player_1
        winner = self.check_win()
        if winner[0]:
            if winner[1] == BoardSpace.PLAYER_1:
                self.winner = self.player_1
            else:
                self.winner = self.player_2
            self.save()
            self.match.create_game()
        return self.json()
        
    def get_valid_moves(self):
        vm = []
        blocker = BoardSpace.PLAYER_1_BLOCKER
        player = BoardSpace.PLAYER_1
        if self.current_turn == self.player_2:
            blocker = BoardSpace.PLAYER_2_BLOCKER
            player = BoardSpace.PLAYER_2
        player_position = self.get_player_position(player)
        for move in MOVE_DIRS:
            x = player_position[0] + move[0]
            y = player_position[1] + move[1]
            try:
                if self.board[x][y] == BoardSpace.EMPTY:
                    vm.append([x,y])
            except IndexError:
                pass
        for jump in JUMP_DIRS:
            x = player_position[0] + jump[0]
            y = player_position[1] + jump[1]
            x2 = x + jump[0]
            y2 = y + jump[1]
            try:
                if self.board[x][y] == blocker and self.board[x2][y2] == BoardSpace.EMPTY:
                    vm.append([x2,y2])
            except IndexError:
                pass
        
        return vm
        
    def get_player_position(self, player):
        for x, row in enumerate(self.board):
            for y, space in enumerate(row):
                if space == player:
                    return [x,y]
        
    def check_win(self):
        win = [False, None]
        p1 = self.get_player_position(BoardSpace.PLAYER_1)
        p2 = self.get_player_position(BoardSpace.PLAYER_2)
        if p1[0] == 0:
            win[0] = True
            win[1] = BoardSpace.PLAYER_1
            return win
        if p2[0] == 7:
            win[0] = True
            win[1] = BoardSpace.PLAYER_2
            return win
        if len(self.get_valid_moves()) == 0:
            win[0] = True
            if self.current_turn == self.player_1:
                win[1] = BoardSpace.PLAYER_2
            else:
                win[1] = BoardSpace.PLAYER_1
        return win
    
    def json(self):
        json_data = {}
        player_1 = {}
        player_2 = {}
        match = {}
        return json_data
        
    
class MoveManager(models.Manager):
    
    def create_move(self, game, player, move_info):
        move_number = game.moves.all().count()
        m = Move.objects.create(
            game=game,
            player = player,
            move_type = move_info['move_type'],
            move_number = move_number,
            move_x_pos = move_info['move_position'][0],
            move_y_pos = move_info['move_position'][1]
        )
        m.save()
    
class Move(models.Model):
    game = models.ForeignKey(Game, related_name="moves")
    player = models.ForeignKey(UserProfile, related_name='player')
    move_type = models.IntegerField(choices=MOVE_TYPES)
    move_number = models.IntegerField()
    move_x_pos = models.IntegerField()
    move_y_pos = models.IntegerField()
    
    objects = MoveManager()
    
                
                