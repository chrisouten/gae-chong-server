from jsonrpc import jsonrpc_method

from account.models import UserProfile

@jsonrpc_method('account.login')
def account_login(request, phone_id):
    try:
        user = UserProfile.objects.get_user(phone_id)
    except UserProfile.DoesNotExist:
        user = UserProfile.objects.create_userprofile(phone_id)
    return user