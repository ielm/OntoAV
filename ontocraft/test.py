from ontoagent.agent import Agent
from ontoagent.utils.analysis import Analyzer
from ontocraft.effectors.move import MoveAMR, MoveEffector
from ontocraft.observers.observer import MalmoObserver
from ontocraft.observers.position import PositionAnalyzer, PositionExecutable
from ontocraft.observers.vision import OcclusionVisionAnalyzer
from ontocraft.utils.MalmoUtils import bootstrap
from ontograph.Frame import Frame

import time


if __name__ == "__main__":

    # Connect to the host
    host = bootstrap(("ontocraft.resources", "test.xml"))
    host.sendCommand("hotbar.9 1")
    time.sleep(0.5)

    # Build a new agent
    agent = Agent.build()
    agent.load_knowledge("ontocraft.resources", "malmo.knowledge")

    move_effector = MoveEffector.build()
    agent.add_effector(move_effector)
    Agent.malmo_host = host

    Analyzer.register_analyzer(PositionAnalyzer)
    Analyzer.register_analyzer(OcclusionVisionAnalyzer)
    agent.add_response(Frame("@ONT.MOTION-EVENT"), PositionExecutable)

    # Observer location and surroundings
    MalmoObserver().observe(agent, join=True)

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

    agent.output(amr, move_effector, join=True)
