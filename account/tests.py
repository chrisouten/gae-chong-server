from django.test import TestCase

from account.models import UserProfile

class AccountTest(TestCase):
    def setUp(self):
        self.u1 = UserProfile.objects.create_userprofile('12345')
        self.u2 = UserProfile.objects.create_userprofile('54321')
        self.u3 = UserProfile.objects.create_userprofile('00000')
    
    def test_random_user(self):
        random_user = UserProfile.objects.get_random_user(self.u1.id)
        self.assertNotEqual(random_user, self.u1)

    def test_get_user(self):
        u = UserProfile.objects.get_user(self.u1.phone_id)
        self.assertEqual(u, self.u1)
      
    def test_user_json(self):
        u = UserProfile.objects.get_user(self.u1.phone_id)
        u = u.json()
        self.assertEqual(u['phone_id'], self.u1.phone_id)
        self.assertEqual(u['id'], self.u1.id)