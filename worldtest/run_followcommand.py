from ontocraft.agent import MalmoAgent
from ontocraft.effectors.move import MoveAMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.utils.MalmoUtils import OntoCraftAgentHost, bootstrap
from ontoagent.engine.executable import HandleExecutable
from ontocraft.observers.position import PositionXMR


from clagent.agent import CLAgent

import time


def follow_command():
	fwd = False
	while (True):
		if (not fwd):
			s = input()
		facing = agent.facing()

		agent.observe(join=True)

		if (s == "keep moving forward"):
			fwd = True

		if (s == "stop"):
			fwd = False

		if (s == "move forward" or fwd):
			# print(facing)
			road  = ""
			clear_road = False
			if (facing == PositionXMR.Facing.SOUTH):
				# the next block to walk on
				road = agent.environment().relative_block(agent, 0, -1, 1).type()
				# whether is the front road is blocked
				clear_road = (agent.environment().relative_block(agent, 0, 0, 1).type() == "")
			elif (facing == PositionXMR.Facing.WEST):
				road = agent.environment().relative_block(agent,1,-1,0).type()
				clear_road = (agent.environment().relative_block(agent,1,0,0).type() == "")
			elif (facing == PositionXMR.Facing.EAST):
				road = agent.environment().relative_block(agent,-1,-1,0).type()
				clear_road = (agent.environment().relative_block(agent,1,0,0).type() == "")
			elif (facing == PositionXMR.Facing.NORTH):
				road = agent.environment().relative_block(agent, 0, -1, -1).type()
				clear_road = (agent.environment().relative_block(agent, 0, 0, -1).type() == "")
		
			if (road == "stone" and clear_road):
				agent.movepath('fx1')
			else:
				tmr = SpeechTMR.build("I cannot move this way, it is not a valid path")
				agent.speak(tmr, join=True)
				fwd = False
		elif (s == "turn right"):
			agent.movepath('cwx1')
		elif (s == "turn left"):
			agent.movepath('ccwx1')
		elif (s == "back up"):
			if (facing == PositionXMR.Facing.SOUTH):
				# the next block to walk on
				road = agent.environment().relative_block(agent, 0, -1, -1).type()
				# whether is the front road is blocked
				clear_road = (agent.environment().relative_block(agent, 0, 0, -1).type() == "")
			elif (facing == PositionXMR.Facing.WEST):
				road = agent.environment().relative_block(agent,-1,-1,0).type()
				clear_road = (agent.environment().relative_block(agent,-1,0,0).type() == "")
			elif (facing == PositionXMR.Facing.EAST):
				road = agent.environment().relative_block(agent,1,-1,0).type()
				clear_road = (agent.environment().relative_block(agent,1,0,0).type() == "")
			elif (facing == PositionXMR.Facing.NORTH):
				road = agent.environment().relative_block(agent, 0, -1, 1).type()
				clear_road = (agent.environment().relative_block(agent, 0, 0, 1).type() == "")
		
			if (road == "stone" and clear_road):
				agent.movepath('bx1')
			else:
				tmr = SpeechTMR.build("I cannot move this way, it is not a valid path")
				agent.speak(tmr, join=True)
		elif (s == 'turn around'):
			agent.movepath('cwx2')



if __name__ == '__main__':
	host = bootstrap(("worldtest.resources", "world.xml"))
	host.sendCommand("hotbar.9 1")
	time.sleep(0.5)

	# Build a new agent
	agent = CLAgent.build(host,None)
	print(agent.anchor["HAS-NAME"].singleton())

	# Observe location and surroundings
	agent.observe(join=True)

	# After the user communicates to the agent that they want to visit the pharmacy, the agent
	# communicates to the user the decision that was made before planning a new route.
	tmr = SpeechTMR.build("OK, I will go to the pharmacy, and then go to the grocery store.")
	agent.speak(tmr, join=True)

	follow_command()

	
		



