import hlt
from hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
import random
import logging

myID, game_map = hlt.get_init()
hlt.send_init("ImpRandomPythonBot")

logger = logging.getLogger(__name__)
logging.basicConfig(filename='ImpRandomPythonBot.log',level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TURN = 1
PROD_WAIT = 5

def set_move(square):
    for direction, neighbor in enumerate(game_map.neighbors(square)):
        if neighbor.owner != myID and neighbor.strength < square.strength:
            logging.info("{} is less than {}, capturing in {}".format(neighbor, square, direction))
            return Move(square, direction)

    if square.strength < PROD_WAIT * square.production:
        logging.info("{} is less than {} * production, staying still".format(square, PROD_WAIT))
        return Move(square, STILL)
    else:
        logging.info("{} is moving randomly".format(square))
        return Move(square, random.choice((NORTH, WEST, STILL)))


while True:
    logging.info("TURN: {}".format(TURN))
    game_map.get_frame()
    moves = [set_move(square) for square in game_map if square.owner == myID]
    TURN += 1
    hlt.send_frame(moves)
