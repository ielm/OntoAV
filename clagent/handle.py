

from ontoagent.agent import Agent
from ontoagent.engine.executable import HandleExecutable
from ontoagent.engine.signal import Signal, XMR
from ontograph.Frame import Frame
from ontograph import graph
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.observers.chat import ChatTMR
from clagent.agent import CLAgent
from ontocraft.observers.position import PositionXMR



class CommandHandleExecutable(HandleExecutable):

	def validate(self, agent: CLAgent, signal: Signal) -> bool:
		return signal.root() ^ Frame("@ONT.SPEECH-ACT") and signal.root()["THEME"].singleton() ^ Frame("@ONT.RAW-TEXT") and signal.agent().id == "@ENV.AGENT.1"

	def run(self, agent: CLAgent, signal: ChatTMR):
		text = signal.raw_text()
		if "Ozymandias" in text:
			agent.speak(SpeechTMR.build("Nothing beside remains. Round the decay Of that colossal wreck, boundless and bare The lone and level sands stretch far away."), join=True)
		elif True in list(map(lambda c: c in text.lower(), ["move", "walk", "turn", "go"])):
			self.parse_command(agent, text)
		else:
			agent.speak(SpeechTMR.build("I heard %s say '%s'." % (signal.agent().id, text)), join=True)

	@staticmethod
	def parse_command(agent: CLAgent, signal: str):
		command = signal.lower()

		tmr = None
		path = None

		def _get_digits(text):
			return ''.join(filter(lambda x: x.isdigit(), text))

		if True in list(map(lambda c: c in command, ["move", "walk", "go"])):
			agent.observe(join=True)
			facing = agent.facing()
			digit = _get_digits(command)
			digit = "1" if digit == "" else digit
			digit = int(digit)
			if "forward" in command:
				direction = 'fx1'
				# digit = "1" if digit == "" else digit
				# path = "fx" + digit
				tmr = SpeechTMR.build("Moving forward {} step{}".format(digit, "s" if int(digit) > 1 else ""))
		  
			if "backward" in command:
				# digit = _get_digits(command)
				# digit = "1" if digit == "" else digit
				# path = "bx" + digit
				tmr = SpeechTMR.build("Moving backward {} step{}".format(digit, "s" if int(digit) > 1 else ""))
				direction = 'bx1'

			for i in range(digit):
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
					agent.movepath(direction)
				else:
					tmr = SpeechTMR.build("I cannot move this way, it is not a valid path")
					agent.speak(tmr, join=True)

		if True in list(map(lambda c: c in command, ["turn", "look"])):
			if True in list(map(lambda c: c in command, ["right", "clockwise", "cw"])):
				print ('tr')
				digit = _get_digits(command)
				digit = "1" if digit == "" else digit
				path = "cwx" + digit
				print (digit)
				tmr = SpeechTMR.build("Turning clockwise {} step{}".format(digit, "s" if int(digit) > 1 else ""))
			if True in list(map(lambda c: c in command, ["left", "counterclockwise", "ccw"])):
				digit = _get_digits(command)
				digit = "1" if digit == "" else digit
				path = "ccwx" + digit
				tmr = SpeechTMR.build("Turning counter-clockwise {} step{}".format(digit, "s" if int(digit) > 1 else ""))
		if tmr is not None:
			agent.speak(tmr)
		if path is not None:
			agent.movepath(path)
