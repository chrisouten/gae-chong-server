from jsonrpc import jsonrpc_method

from game.models import Match, Game, Move

@jsonrpc_method('game.create_match')
def create_match(request, phone_id, chonger_2, match_type, public, ranked):
    chonger_1 = UserProfile.objects.get_user(phone_id)
    if chonger_2:
        try:
            chonger_2 = UserProfile.objects.get(id=chonger_2)
        except UserProfile.DoesNotExist:
            chonger_2 = None
    m = Match.objects.create_match(chonger_1.id, chonger_2, match_type, public, ranked)
    return m.json()
    
@jsonrpc_method('game.get_match')
def get_match(request, phone_id, match_id):
    try:
        return Match.objects.get(id=match_id).json()
    except Match.DoesNotExist:
        return {'error': 'Match does not exist'}
