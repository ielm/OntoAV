from ontoagent.agent import Agent
from ontocraft.move import MoveAMR, MoveEffector
from ontocraft.utils.MalmoUtils import bootstrap
import time


if __name__ == "__main__":

    # Connect to the host
    host = bootstrap(("ontocraft", "test.xml"))
    host.sendCommand("hotbar.9 1")
    time.sleep(0.5)

    # Build a new agent
    agent = Agent.build()
    move_effector = MoveEffector.build()
    agent.add_effector(move_effector)
    Agent.malmo_host = host

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

    agent.output(amr, move_effector)
