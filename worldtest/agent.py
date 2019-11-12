from ontocraft.agent import MalmoAgent
from ontocraft.effectors.move import MoveAMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.utils.MalmoUtils import OntoCraftAgentHost, bootstrap

import time


if __name__ == '__main__':
	host = bootstrap(("resources", "world.xml"))
	host.sendCommand("hotbar.9 1")
	time.sleep(0.5)

	# Build a new agent
	agent = MalmoAgent.build(host)
	print(agent.anchor["HAS-NAME"].singleton())

	# Say something
	tmr = SpeechTMR.build("Hello world.")
	agent.speak(tmr, join=True)