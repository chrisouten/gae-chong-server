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
    
    def create_userprofile(self, email, google_id):
        default_display_name = '%s %s %s' % (random.choice(ADJECTIVE_SAMPLES), random.choice(NOUN_SAMPLES), random.choice(VERB_SAMPLES))
        up = self.create(
            email = email,
            google_id = google_id,
            display_name = default_display_name
        )
        return up
    
    def get_user(self, token):
        return self.get(google_id=token)

class UserProfile(models.Model):
    email = models.EmailField()
    google_id = models.CharField(max_length=75)
    display_name = models.CharField(max_length=75)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    rating = models.IntegerField(default=1200)
    
    objects = UserProfileManager()