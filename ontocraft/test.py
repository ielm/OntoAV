from ontocraft.agent import MalmoAgent
from ontocraft.effectors.move import MoveAMR
from ontocraft.utils.MalmoUtils import bootstrap

import time


if __name__ == "__main__":

    # Connect to the host
    host = bootstrap(("ontocraft.resources", "test.xml"))
    host.sendCommand("hotbar.9 1")
    time.sleep(0.5)

    # Build a new agent
    agent = MalmoAgent.build(host)

    # Observe location and surroundings
    agent.observe(join=True)

    # Construct a movement AMR path, and output it
    amr = MoveAMR.build()
    amr.add_to_path_turn_clockwise()
    amr.add_to_path_move_forward()
    amr.add_to_path_turn_counterclockwise()
    amr.add_to_path_move_forward()
    amr.add_to_path_move_forward()
    amr.add_to_path_move_forward()
    amr.add_to_path_move_forward()
    amr.add_to_path_move_forward()

    agent.move(amr, join=True)
