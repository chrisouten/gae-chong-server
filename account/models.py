import random
from itertools import chain

from django.db import models


ADJECTIVE_SAMPLES = [
    'Happy',
    'Sad',
    'Energetic',
    'Adorable',
    'Beautiful',
    'Fancy',
    'Glamorous',
    'Handsome',
    'Long',
    'Magnificent',
    'Sparkling',
]

NOUN_SAMPLES = [
    'Beam',
    'Insurance',
    'Libra',
    'Mitten',
    'Beam',
    'Curtain',
    'Fiber',
    'Frog',
    'Instrument',
    'Mouth',
    'Sweatshirt',
]

VERB_SAMPLES = [
    'Licker',
    'Watcher',
    'Petter',
    'Runner',
    'Hopper',
    'Maker',
]

class UserProfileManager(models.Manager):
    
    def create_userprofile(self, phone_id):
        default_display_name = '%s %s %s' % (random.choice(ADJECTIVE_SAMPLES), random.choice(NOUN_SAMPLES), random.choice(VERB_SAMPLES))
        invalid = True
        while invalid:
            invalid = not self.check_existing_username(default_display_name)
            if invalid:
                default_display_name = '%s %s %s' % (random.choice(ADJECTIVE_SAMPLES), random.choice(NOUN_SAMPLES), random.choice(VERB_SAMPLES))
        up = self.create(
            phone_id = phone_id,
            display_name = default_display_name
        )
        return up
    
    def get_user(self, phone_id):
        return self.get(phone_id=phone_id)

    def check_existing_username(self, name):
        try:
           UserProfile.objects.get(display_name=name)
           return False
        except UserProfile.DoesNotExist:
            return True

class UserProfile(models.Model):
    phone_id = models.CharField(max_length=75)
    display_name = models.CharField(max_length=75)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    rating = models.IntegerField(default=1200)
    
    objects = UserProfileManager()
    
    def json(self):
        up = {}
        up['id'] = self.id
        up['display_name'] = self.display_name
        up['wins'] = self.wins
        up['losses'] = self.losses
        up['rating'] = self.rating
        return up
    
    def get_all_matches(self):
        matches = list(chain(self.chonger_1.all(), self.chonger_2.all()))
        return [m.json() for m in matches]

    def change_username(self, display_name):
        valid = UserProfile.objects.check_existing_username(display_name)
        if valid:
            self.display_name = display_name
            self.save()
            return self.json()
        else:
            return {'error': 'That name is already taken'}
        