from ontoagent.agent import Agent
from ontoagent.utils.analysis import Analyzer
from ontocraft.move import MoveEffector
from ontocraft.position import PositionAnalyzer, PositionExecutable, PositionSignal
from ontocraft.utils.MalmoUtils import bootstrap
from ontocraft.vision import SupervisionAnalyzer, SupervisionSignal
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
    Analyzer.register_analyzer(SupervisionAnalyzer)
    agent.add_response(Frame("@ONT.MOTION-EVENT"), PositionExecutable)

    starting_world_state = host.getWorldState()

    # Anchor physical location
    signal = PositionSignal.build(starting_world_state)
    agent.input(signal, join=True)

    # Observe the surroundings
    start = time.time()
    signal = SupervisionSignal.build(starting_world_state)
    agent.input(signal, join=True)
    print(time.time() - start)

    from ontocraft.vision import MalmoBlock
    block = MalmoBlock(Frame("@ENV.MALMO-BLOCK.1"))
    print(block.type())
    print(block.absx())
    print(block.absy())
    print(block.absz())

    # # Construct a movement AMR path, and output it
    # amr = MoveAMR.build()
    # amr.add_to_path_turn_clockwise()
    # amr.add_to_path_move_forward()
    # amr.add_to_path_turn_counterclockwise()
    # amr.add_to_path_move_forward()
    # amr.add_to_path_move_forward()
    # amr.add_to_path_move_forward()
    # amr.add_to_path_move_forward()
    # amr.add_to_path_move_forward()
    #
    # agent.output(amr, move_effector, join=True)
