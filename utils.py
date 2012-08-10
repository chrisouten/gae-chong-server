from account.models import UserProfile

def chong_authenticate(username, password):
    try:
        return UserProfile.objects.get_user(username)
    except UserProfile.DoesNotExist:
        return None

class FakeRequest(object):
    def __init__(self):
        self.user = None