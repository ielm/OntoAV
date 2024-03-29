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
    host = bootstrap(("tests.resources", "example.xml"))
    host.sendCommand("hotbar.9 1")
    time.sleep(0.5)

    # Build a new agent
    agent = MalmoAgent.build(host)
    print(agent.anchor["HAS-NAME"].singleton())

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

    # Observe the environment again
    agent.observe(join=True)

    # The environment should have a record of the stone_button
    # It is directly in front (relx = 0, relz = 1), and is at eye-level (rely = 1)
    print(agent.environment().relative_block(agent, 0, 1, 1).type())
