from django.test import TestCase

from account.models import UserProfile
from game.models import Match, Game, Move, MATCH_TYPES, BoardSpace

class MatchTest(TestCase):
    def setUp(self):
        self.u1 = UserProfile.objects.create_userprofile('12345')
        self.u2 = UserProfile.objects.create_userprofile('54321')
        self.u3 = UserProfile.objects.create_userprofile('00000')

    def create_match(self):
        return Match.objects.create_match(self.u1.id, None, MATCH_TYPES[1][0], True, True)
    
    def join_match(self):
        Match.objects.create_match(self.u2.id, None, MATCH_TYPES[1][0], True, True)
        
    def test_create_match(self):
        m = self.create_match()
        self.assertNotEqual(m.chonger_2, self.u1)
        self.assertTrue(m.public)

    def test_no_created_game(self):
        m = self.create_match()
        self.assertEqual(m.games.count(), 0)
        
    def test_dont_join_different_match_types(self):
        m = self.create_match()
        m2 = Match.objects.create_match(self.u2.id, None, MATCH_TYPES[0][0], True, True)
        self.assertEqual(m.games.count(), 0)
        self.assertEqual(m2.games.count(), 0)
        
    def test_multiple_matches_created(self):
        m = self.create_match()
        self.join_match()
        m2 = Match.objects.create_match(self.u3.id, None, MATCH_TYPES[1][0], True, True)
        self.assertEqual(m.games.count(), 1)
        self.assertEqual(m2.games.count(), 0)
        
    def test_get_all_matches(self):
        m = self.create_match()
        self.join_match()
        m2 = Match.objects.create_match(self.u3.id, None, MATCH_TYPES[1][0], True, True)
        Match.objects.create_match(self.u1.id, None, MATCH_TYPES[1][0], True, True)
        matches = self.u1.get_all_matches()
        self.assertEqual(len(matches), 2)

    def test_create_game(self):
        m = self.create_match()
        self.join_match()
        self.assertEqual(m.games.count(), 1)

    def test_win_condition(self):
        m = self.create_match()
        self.join_match()
        m.chonger_1_wins = 2
        m.save()
        m.create_game()
        self.assertEqual(m.match_winner, self.u1)

    def test_json(self):
        m = self.create_match()
        self.join_match()
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
        m = Match.objects.create_match(self.u1.id, None, MATCH_TYPES[1][0], True, True)
        self.join_match()
        return m
        
    def join_match(self):
        Match.objects.create_match(self.u2.id, None, MATCH_TYPES[1][0], True, True)

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