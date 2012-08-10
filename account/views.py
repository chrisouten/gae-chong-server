from jsonrpc import jsonrpc_method

from account.models import UserProfile
from utils import chong_authenticate

@jsonrpc_method('account.login')
def login(request, phone_id):
    try:
        user = UserProfile.objects.get_user(phone_id)
    except UserProfile.DoesNotExist:
        user = UserProfile.objects.create_userprofile(phone_id)
    user_json = user.json()
    user_json['phone_id'] = user.phone_id
    return user_json

@jsonrpc_method('account.get_all_matches', authenticated=chong_authenticate)
def get_all_matches(request):
    return request.user.get_all_matches()
    
@jsonrpc_method('account.get_user_by_name', authenticated=chong_authenticate)
def get_user_by_name(request, display_name):
    display_name = display_name.strip()
    try:
        user = UserProfile.objects.get(display_name=display_name).json()
        return user
    except UserProfile.DoesNotExist:
        return {'error': 'User Not Found'}
        
@jsonrpc_method('account.change_user_name', authenticated=chong_authenticate)
def change_user_name(request, display_name):
    return request.user.change_username(display_name)
    
   
    