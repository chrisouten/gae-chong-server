from django.test import TestCase

from account.models import UserProfile
from game.models import Match, Game, Move, MATCH_TYPES, BoardSpace

class MatchTest(TestCase):
    def setUp(self):
        self.u1 = UserProfile.objects.create_userprofile('12345')
        self.u2 = UserProfile.objects.create_userprofile('54321')
        self.u3 = UserProfile.objects.create_userprofile('00000')

    def create_match(self):
        return Match.objects.create_match(self.u1.id, None, MATCH_TYPES[1][0], True)
        
    def test_create_match(self):
        m = self.create_match()
        self.assertNotEqual(m.chonger_2, self.u1)
        self.assertTrue(m.public)

    def test_create_game(self):
        m = self.create_match()
        self.assertEqual(m.games.count(), 1)

    def test_win_condition(self):
        m = self.create_match()
        m.chonger_1_wins = 2
        m.save()
        m.create_game()
        self.assertEqual(m.match_winner, self.u1)

    def test_json(self):
        m = self.create_match()
        mj = m.json()
        self.assertEqual(mj['chonger_1']['id'], self.u1.id)
        self.assertEqual(mj['match_type'], MATCH_TYPES[1][0])
        self.assertEqual(mj['chonger_2_wins'], 0)
        self.assertEqual(mj['match_winner'], None)
        
class GameTest(TestCase):
    
    def setUp(self):
        self.u1 = UserProfile.objects.create_userprofile('12345')
        self.u2 = UserProfile.objects.create_userprofile('54321')
        self.u3 = UserProfile.objects.create_userprofile('00000')

    def create_match(self):
        return Match.objects.create_match(self.u1.id, None, MATCH_TYPES[1][0], True)

    def test_switch_p1_p2_on_next_game(self):
        m = self.create_match()
        op1 = m.games.all()[0].player_1
        op2 = m.games.all()[0].player_2
        m.create_game()
        self.assertEqual(m.games.all()[1].player_1, m.games.all()[0].player_2)
        self.assertEqual(m.games.all()[1].player_2, m.games.all()[0].player_1)

    def test_initial_valid_moves(self):
        m = self.create_match()
        g = m.games.all()[0]
        self.assertEqual(len(g.get_valid_moves()), 3)

    def test_jump_valid_moves(self):
        m = self.create_match()
        g = m.games.all()[0]
        op1 = g.get_player_position(1)
        g.board[6][3] = BoardSpace.PLAYER_1_BLOCKER
        g.save()
        self.assertEqual(len(g.get_valid_moves()), 4)

    def test_get_player_position(self):
        m = self.create_match()
        g = m.games.all()[0]
        self.assertEqual(g.get_player_position(1),[7,4])

    def test_check_win(self):
        m = self.create_match()
        g = m.games.all()[0]
        op1 = g.get_player_position(1)
        g.board[op1[0]][op1[1]] = BoardSpace.EMPTY
        g.board[0][4] = BoardSpace.PLAYER_1
        g.save()
        self.assertTrue(g.check_win()[0])
        self.assertEqual(g.check_win()[0], 1)

    def test_making_invalid_move(self):
        m = self.create_match()
        g = m.games.all()[0]
        result = g.make_move(g.player_1.phone_id, {'move_type':1, 'move_position':[6,3]})
        self.assertTrue(result.has_key('error'))

    def test_making_valid_pawn_move(self):
        m = self.create_match()
        g = m.games.all()[0]
        result = g.make_move(g.player_1.phone_id, {'move_type':1, 'move_position':[6,4]})
        self.assertFalse(result.has_key('error'))
        self.assertEqual(g.board[6][4], 1)


    def test_making_valid_blocker_move(self):
        m = self.create_match()
        g = m.games.all()[0]
        result = g.make_move(g.player_1.phone_id, {'move_type':3, 'move_position':[4,4]})
        self.assertFalse(result.has_key('error'))
        self.assertEqual(g.board[4][4], 3)

    def test_json(self):
        pass