import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random
import logging

TURN = 1
PROD_WAIT = 4 #random.randint(4, 6) # still tuning how long to delay move
NAME = "OK_256_PythonBot_w" + str(PROD_WAIT)
CARDINALS = [NORTH, EAST, SOUTH, WEST]

myID, game_map = hlt.get_init()
hlt.send_init(NAME)

logger = logging.getLogger(__name__)
logging.basicConfig(filename=('zLOG_' + NAME + '.log'),level=logging.WARNING,
                    format='%(levelname)s - %(message)s')

def find_near_enemy(square):
    direction = NORTH
    max_dist = min(game_map.width, game_map.height) / 2

    for d in CARDINALS:
        distance = 0
        current = square;
        while current.owner == myID and distance < max_dist:
            distance += 1
            current = game_map.get_target(current, d) #hmm
        if distance < max_dist:
            direction = d
            max_dist = distance
    logging.info("{} is moving towards {}".format(square, direction))
    return direction

def heuristic(square):
    if square.owner == 0:
        if square.strength:
            return square.production / square.strength
        else:
            return square.production
    else:
        # return total potential damage caused by overkill when attacking this square
        return sum(neighbor.strength for neighbor in game_map.neighbors(square) if neighbor.owner not in (0, myID))

def avoid_256(square, direction):
    t_sq = game_map.get_target(square, direction)
    if t_sq.owner != myID:
        return direction
    else:
        if t_sq.strength + square.strength > 255:
            return random.choice(list(filter((direction).__ne__, CARDINALS)))
        else:
            return direction


def set_move(square):
    target, direction = max(((neighbor, direction) for direction, neighbor in enumerate(game_map.neighbors(square))
                            if neighbor.owner != myID),
                            default = (None, None),
                            key = lambda t: heuristic(t[0]))
    if target is not None and target.strength < square.strength:
        logging.info("{} is less than {}, capturing in {}".format(target, square, direction))
        return Move(square, avoid_256(square, direction))

    elif square.strength < PROD_WAIT * square.production:
        logging.info("{} is less than {} * production, staying still".format(square, PROD_WAIT))
        return Move(square, STILL)

    border = any(neighbor.owner != myID for neighbor in game_map.neighbors(square))
    if not border:
        logging.info("{} is moving towards enemy".format(square))
        return Move(square, avoid_256(square, find_near_enemy(square)))
    else:
        logging.info("{} staying still".format(square))
        return Move(square, STILL)


while True:
    logging.info("TURN: {}".format(TURN))
    game_map.get_frame()
    moves = [set_move(square) for square in game_map if square.owner == myID]
    TURN += 1
    hlt.send_frame(moves)
