from ontocraft.agent import MalmoAgent
from ontocraft.effectors.move import MoveAMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.utils.MalmoUtils import bootstrap

import time

"""
To run this example script:

1) Follow the installation instructions in the README
2) Follow the Running an Agent instructions in the README
3) Set your environment to have the following variable (located in your Malmo installation):
   MALMO_XSD_PATH = path/to/MalmoPlatform/Schemas/
4) Run this file
"""

if __name__ == "__main__":

    # Connect to the host
    host = bootstrap(("ontocraft.resources", "test.xml"))
    host.sendCommand("hotbar.9 1")
    time.sleep(0.5)

    # Build a new agent
    agent = MalmoAgent.build(host)

    # Observe location and surroundings
    agent.observe(join=True)

    # Say something
    tmr = SpeechTMR.build("Hello world.")
    agent.speak(tmr, join=True)

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
