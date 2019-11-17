from ontocraft.agent import MalmoAgent
from ontocraft.effectors.move import MoveAMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.utils.MalmoUtils import OntoCraftAgentHost, bootstrap
from pkgutil import get_data
from clagent.agent import CLAgent

import time


if __name__ == '__main__':
	map_file = ("worldtest.resources", "map.txt")

	host = bootstrap(("worldtest.resources", "world.xml"))
	host.sendCommand("hotbar.9 1")
	time.sleep(0.5)

	# Build a new agent
	agent = CLAgent.build(host, ("worldtest.resources", "map.txt"))
	agent.navigate_to('G')

	# agent.movepath("fx18, cwx1, fx12, cwx1")

	# Say something
	# agent.speaksentence("Hello world.")

