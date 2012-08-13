from django.test import TestCase

from account.models import UserProfile
from game.models import Match, Game, Move, MATCH_TYPES, BoardSpace
from game.views import *
from utils import FakeRequest

class MatchTest(TestCase):
    def setUp(self):
        self.u1 = UserProfile.objects.create_userprofile('12345')
        self.u2 = UserProfile.objects.create_userprofile('54321')
        self.u3 = UserProfile.objects.create_userprofile('00000')

    def create_match(self):
        return Match.objects.create_match(self.u1, None, MATCH_TYPES[1][0], True, True)

    def join_match(self):
        Match.objects.create_match(self.u2, None, MATCH_TYPES[1][0], True, True)
        
    def test_create_match_both_players(self):
        m = Match.objects.create_match(self.u1, self.u2, MATCH_TYPES[1][0], True, True)
        self.assertEqual(m.chonger_1, self.u1)
        self.assertEqual(m.chonger_2, self.u2)
        self.assertEqual(m.games.count(), 1)

    def test_create_match(self):
        m = self.create_match()
        self.assertNotEqual(m.chonger_2, self.u1)
        self.assertTrue(m.public)

    def test_no_created_game(self):
        m = self.create_match()
        self.assertEqual(m.games.count(), 0)
        
    def test_dont_join_different_match_types(self):
        m = self.create_match()
        m2 = Match.objects.create_match(self.u2, None, MATCH_TYPES[0][0], True, True)
        self.assertEqual(m.games.count(), 0)
        self.assertEqual(m2.games.count(), 0)
        
    def test_multiple_matches_created(self):
        m = self.create_match()
        self.join_match()
        m2 = Match.objects.create_match(self.u3, None, MATCH_TYPES[1][0], True, True)
        self.assertEqual(m.games.count(), 1)
        self.assertEqual(m2.games.count(), 0)
        
    def test_get_all_matches(self):
        m = self.create_match()
        self.join_match()
        m2 = Match.objects.create_match(self.u3, None, MATCH_TYPES[1][0], True, True)
        Match.objects.create_match(self.u1, None, MATCH_TYPES[1][0], True, True)
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
        self.assertEqual(mj['match_type'], MATCH_TYPES[1][1])
        self.assertEqual(mj['chonger_2_wins'], 0)
        self.assertEqual(mj['match_winner'], None)
        
class GameTest(TestCase):
    
    def setUp(self):
        self.u1 = UserProfile.objects.create_userprofile('12345')
        self.u2 = UserProfile.objects.create_userprofile('54321')
        self.u3 = UserProfile.objects.create_userprofile('00000')

    def create_match(self):
        m = Match.objects.create_match(self.u1, None, MATCH_TYPES[1][0], True, True)
        self.join_match()
        return m
        
    def join_match(self):
        Match.objects.create_match(self.u2, None, MATCH_TYPES[1][0], True, True)

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
        result = g.make_move(g.player_1, {'move_type':1, 'move_position':[6,3]})
        self.assertTrue(result.has_key('error'))

    def test_making_valid_pawn_move(self):
        m = self.create_match()
        g = m.games.all()[0]
        result = g.make_move(g.player_1, {'move_type':1, 'move_position':[6,4]})
        self.assertFalse(result.has_key('error'))
        self.assertEqual(g.board[6][4], 1)


    def test_making_valid_blocker_move(self):
        m = self.create_match()
        g = m.games.all()[0]
        result = g.make_move(g.player_1, {'move_type':3, 'move_position':[4,4]})
        self.assertFalse(result.has_key('error'))
        self.assertEqual(g.board[4][4], 3)

    def test_json(self):
        pass

class GameViewTest(TestCase):

    def setUp(self):
        self.u1 = self.create_user('1')
        self.u2 = self.create_user('2')
        self.u3 = self.create_user('3')

    def create_user(self, phone_id):
        return UserProfile.objects.create_userprofile(phone_id)

    def test_create_match(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, self.u2.id, 1, True, True)        
        self.assertEqual(m['chonger_1']['id'], self.u1.id)
        self.assertEqual(m['chonger_2']['id'], self.u2.id)

    def test_create_match_no_user(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, None, 1, True, True)
        self.assertEqual(m['chonger_1']['id'], self.u1.id)
        self.assertEqual(m['chonger_2'], None)

    def test_create_match_invalid_user(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, 12345, 1, True, True)
        self.assertTrue('error' in m.keys())

    def test_value_error_create_match(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, 'valueerror', 1, True, True)
        self.assertTrue('error' in m.keys())

    def test_get_match(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, self.u2.id, 1, True, True)
        gm = get_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, m['id'])
        self.assertEqual(gm['id'], m['id'])
        self.assertEqual(gm['chonger_1']['id'], self.u1.id)
        self.assertEqual(gm['chonger_2']['id'], self.u2.id)

    def test_get_match_no_c2(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, None, 1, True, True)
        gm = get_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, m['id'])
        self.assertEqual(gm['id'], m['id'])
        self.assertEqual(gm['chonger_1']['id'], self.u1.id)
        self.assertEqual(gm['chonger_2'], None)
    
    def test_get_match_value_error(self):
        gm = get_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, 'valueerror')
        self.assertTrue('error' in gm.keys())

    def test_get_game(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, self.u2.id, 1, True, True)
        gg = get_game(FakeRequest(), self.u1.phone_id, self.u1.phone_id, m['games'][0]['id'])
        self.assertEqual(gg['id'], m['games'][0]['id'])

    def test_get_game_na(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, None, 1, True, True)
        gg = get_game(FakeRequest(), self.u1.phone_id, self.u1.phone_id, 954651)
        self.assertTrue('error' in gg.keys())

    def test_get_game_value_error(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, self.u2.id, 1, True, True)
        gg = get_game(FakeRequest(), self.u1.phone_id, self.u1.phone_id, 'valueerror')
        self.assertTrue('error' in gg.keys())

    def test_submit_move(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, self.u2.id, 1, True, True)
        gg = get_game(FakeRequest(), self.u1.phone_id, self.u1.phone_id, m['games'][0]['id'])
        cp = UserProfile.objects.get(id=gg['current_turn']['id'])
        move_info = {'move_type':1, 'move_position':[6,4]}
        sm = submit_move(FakeRequest, cp.phone_id, cp.phone_id, gg['id'], move_info)
        self.assertEqual(sm['current_turn']['id'], gg['player_2']['id'])

    def test_invalid_block_placement(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, self.u2.id, 1, True, True)
        gg = get_game(FakeRequest(), self.u1.phone_id, self.u1.phone_id, m['games'][0]['id'])
        cp = UserProfile.objects.get(id=gg['current_turn']['id'])
        move_info = {'move_type':3, 'move_position':[7,3]}
        sm = submit_move(FakeRequest, cp.phone_id, cp.phone_id, gg['id'], move_info)
        self.assertTrue('error' in sm.keys())
        move_info['move_position'] = [7,4]
        sm = submit_move(FakeRequest, cp.phone_id, cp.phone_id, gg['id'], move_info)
        self.assertTrue('error' in sm.keys())
        move_info['move_position'] = [0,4]
        sm = submit_move(FakeRequest, cp.phone_id, cp.phone_id, gg['id'], move_info)
        self.assertTrue('error' in sm.keys())

    def test_invalid_move_placement(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, self.u2.id, 1, True, True)
        gg = get_game(FakeRequest(), self.u1.phone_id, self.u1.phone_id, m['games'][0]['id'])
        cp = UserProfile.objects.get(id=gg['current_turn']['id'])
        move_info = {'move_type':1, 'move_position':[1,4]}
        sm = submit_move(FakeRequest, cp.phone_id, cp.phone_id, gg['id'], move_info)
        self.assertTrue('error' in sm.keys())

    def test_invalid_move_info(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, self.u2.id, 1, True, True)
        gg = get_game(FakeRequest(), self.u1.phone_id, self.u1.phone_id, m['games'][0]['id'])
        cp = UserProfile.objects.get(id=gg['current_turn']['id'])
        move_info = {'move_type':1}
        sm = submit_move(FakeRequest, cp.phone_id, cp.phone_id, gg['id'], move_info)
        self.assertTrue('error' in sm.keys())
        move_info = {'move_type':99}
        sm = submit_move(FakeRequest, cp.phone_id, cp.phone_id, gg['id'], move_info)
        self.assertTrue('error' in sm.keys())

    def test_wrong_player_turn(self):
        m = create_match(FakeRequest(), self.u1.phone_id, self.u1.phone_id, self.u2.id, 1, True, True)
        gg = get_game(FakeRequest(), self.u1.phone_id, self.u1.phone_id, m['games'][0]['id'])
        cp = UserProfile.objects.get(id=gg['player_2']['id'])
        move_info = {'move_type':1, 'move_position':[6,4]}
        sm = submit_move(FakeRequest, cp.phone_id, cp.phone_id, gg['id'], move_info)
        self.assertTrue('error' in sm.keys())

    def test_move_value_error(self):
        sm = submit_move(FakeRequest, self.u1.phone_id, self.u1.phone_id, 'aadfasd',{})
        self.assertTrue('error' in sm.keys())


