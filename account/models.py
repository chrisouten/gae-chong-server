import random

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
        up = self.create(
            phone_id = phone_id,
            display_name = default_display_name
        )
        return up
    
    def get_user(self, phone_id):
        return self.get(phone_id=phone_id)

    def get_random_user(self, originator):
        users = self.exclude(id=originator)
        count = users.count()
        return users[random.randint(0, count -1)]

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
        up['phone_id'] = self.phone_id
        up['display_name'] = self.display_name
        up['wins'] = self.wins
        up['losses'] = self.losses
        up['rating'] = self.rating
        return up
    
        
        