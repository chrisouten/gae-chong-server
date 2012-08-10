from django.test import TestCase

from account.models import UserProfile
from account.views import *
from game.models import Match
from utils import FakeRequest

class AccountTest(TestCase):
    def setUp(self):
        self.u1 = UserProfile.objects.create_userprofile('12345')
        self.u2 = UserProfile.objects.create_userprofile('54321')
        self.u3 = UserProfile.objects.create_userprofile('00000')
    
    def test_get_user(self):
        u = UserProfile.objects.get_user(self.u1.phone_id)
        self.assertEqual(u, self.u1)
      
    def test_user_json(self):
        u = UserProfile.objects.get_user(self.u1.phone_id)
        u = u.json()
        self.assertEqual(u['display_name'], self.u1.display_name)
        self.assertEqual(u['id'], self.u1.id)
        
    def test_change_user_name(self):
        result = self.u1.change_username('Cool Dude')
        self.assertEqual('Cool Dude', result['display_name'])
        self.assertEqual('Cool Dude', UserProfile.objects.get(phone_id=self.u1.phone_id).display_name)
        
    def test_change_user_name_fail(self):
        result = self.u1.change_username(self.u2.display_name)
        self.assertTrue(result.has_key('error'))
        
class AccountViewTest(TestCase):
    
    def create_user(self, phone_id):
        return UserProfile.objects.create_userprofile(phone_id)

    def test_create_user(self):
        result = login(FakeRequest(), '12345')
        self.assertEqual(result['phone_id'], '12345')

    def test_change_user_name(self):
        u1 = self.create_user('12345')
        result = change_user_name(FakeRequest(), '12345','12345','omg')
        self.assertEqual(result['display_name'], 'omg')

    def test_change_user_name_error(self):
        u1 = self.create_user('12345')
        u2 = self.create_user('54321')
        result = change_user_name(FakeRequest(), '12345','12345', u2.display_name)
        self.assertTrue('error' in result.keys())

    def test_get_all_matches(self):
        u1 = self.create_user('12345')
        u2 = self.create_user('54321')
        m = Match.objects.create_match(u1,u2,1,True,True)
        result = get_all_matches(FakeRequest(), u1.phone_id, u1.phone_id)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['chonger_1']['display_name'], u1.display_name)

    def test_get_user_by_name(self):
        u1 = self.create_user('12345')
        u2 = self.create_user('54321')
        result = get_user_by_name(FakeRequest(), u1.phone_id, u1.phone_id, u2.display_name)
        self.assertEqual(result['display_name'], u2.display_name)
        self.assertEqual(result['id'], u2.id)

    def test_get_user_by_name_extra_spaces(self):
        u1 = self.create_user('12345')
        u2 = self.create_user('54321')
        result = get_user_by_name(FakeRequest(), u1.phone_id, u1.phone_id, ' %s      ' % u2.display_name)
        self.assertEqual(result['display_name'], u2.display_name)
        self.assertEqual(result['id'], u2.id)

    def test_get_user_wrong_name(self):
        u1 = self.create_user('12345')
        u2 = self.create_user('54321')
        result = get_user_by_name(FakeRequest(), u1.phone_id, u1.phone_id, 'fakename')
        self.assertTrue('error' in result.keys())
