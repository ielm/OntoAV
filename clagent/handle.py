

from ontoagent.agent import Agent
from ontoagent.engine.executable import HandleExecutable
from ontoagent.engine.signal import Signal, XMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.observers.chat import ChatTMR
from ontocraft.observers.position import PositionXMR



class ChatHandleExecutable(HandleExecutable):

	def validate(self, agent: Agent, signal: Signal) -> bool:
		return True

	def run(self, agent: Agent, signal: ChatTMR):
		tmr = SpeechTMR.build("I heard %s say '%s'." % (signal.agent().id, signal.raw_text()))
		agent.speak(tmr, join=True)

		############
		s = signal.raw_text()

		agent.observe(join=True)

		facing = agent.facing()

		if (s == "move forward"):
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
				# fwd = False
		elif (s == "turn right"):
			print ('tr')
			agent.movepath('cwx1')
		elif (s == "turn left"):
			agent.movepath('ccwx1')
		elif (s == "back up"):
			if (facing == PositionXMR.Facing.SOUTH):
				# the next block to walk on
				raod = agent.environment().relative_block(agent, 0, -1, -1).type()
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

