from ontocraft.agent import MalmoAgent
from ontocraft.effectors.move import MoveAMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.utils.MalmoUtils import OntoCraftAgentHost, bootstrap

import time

class OntoAV:

    def __init__(self, agent: MalmoAgent=None, host: OntoCraftAgentHost=None, effectors: list=None):
        if host is None:
            self.host = bootstrap(("resources", "world.xml"))
            self.host.sendCommand("hotbar.9 1")
            time.sleep(0.5)
        if agent is None:
            self.agent = MalmoAgent.build()
            print(agent.anchor["HAS-NAME"].singleton())

        # TODO:
        #   [] - Do something with effectors
        #   [] - Build utilities for building movement AMRs paths automatically
        #   [] - Build utilities for moving, observing, and generating output (speech and movement)

