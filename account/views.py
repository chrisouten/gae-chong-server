from jsonrpc import jsonrpc_method

from account.models import UserProfile

def mah_authenticate(username, password):
    try:
        return UserProfile.objects.get_user(username)
    except UserProfile.DoesNotExist:
        return None

@jsonrpc_method('account.login')
def login(request, phone_id):
    try:
        user = UserProfile.objects.get_user(phone_id)
    except UserProfile.DoesNotExist:
        user = UserProfile.objects.create_userprofile(phone_id)
    return user

@jsonrpc_method('account.get_all_matches')
def get_all_matches(request, phone_id):
    return UserProfile.objects.get_user(phone_id).get_all_matches()
    
@jsonrpc_method('account.get_user_by_name', authenticated=mah_authenticate)
def get_user_by_name(request, display_name):
    display_name = display_name.strip()
    try:
        user = UserProfile.objects.get(display_name=display_name)
    except UserProfile.DoesNotExist:
        return {'error': 'User Not Found'}
        
@jsonrpc_method('account.change_user_name')
def change_user_name(request, phone_id, display_name):
    return UserProfile.objects.change_user_name(phone_id, display_name)
    
   
    