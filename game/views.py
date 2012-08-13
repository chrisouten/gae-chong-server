from jsonrpc import jsonrpc_method

from account.models import UserProfile
from game.models import Match, Game, Move
from utils import chong_authenticate

@jsonrpc_method('game.create_match', authenticated=chong_authenticate)
def create_match(request, chonger_2, match_type, public, ranked):
    if chonger_2:
        try:
            chonger_2 = UserProfile.objects.get(id=chonger_2)
        except UserProfile.DoesNotExist:
            return {'error':'Could not find that opponent'}
        except ValueError:
            return {'error':'Must submit an integer for opponent id'}
    else:
        chonger_2 = None
    m = Match.objects.create_match(request.user, chonger_2, match_type, public, ranked)
    return m.json()
    
@jsonrpc_method('game.get_match', authenticated=chong_authenticate)
def get_match(request, match_id):
    try:
        return Match.objects.get(id=match_id).json()
    except Match.DoesNotExist:
        return {'error': 'Match does not exist'}
    except ValueError:
        return {'error': 'Must submit an integer for match id'}

@jsonrpc_method('game.get_game', authenticated=chong_authenticate)
def get_game(request, game_id):
    try:
        return Game.objects.get(id=game_id).json()
    except Game.DoesNotExist:
        return {'error':'Game does not exist'}
    except ValueError:
        return {'error': 'Must submit an integer for game id'}

@jsonrpc_method('game.submit_move', authenticated=chong_authenticate)
def submit_move(request, game_id, move_info):
    try:
        g = Game.objects.get(id=game_id)
        return g.make_move(request.user, move_info)
    except Game.DoesNotExist:
        return {'error':'Game does not exist'}
    except ValueError:
        return {'error': 'Must submit an integer for game id'}
