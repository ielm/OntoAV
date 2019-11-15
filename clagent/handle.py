from ontoagent.agent import Agent
from ontoagent.engine.executable import HandleExecutable
from ontoagent.engine.signal import Signal, XMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.observers.chat import ChatTMR
# from clagent.agent import CLAgent


class ChatHandleExecutable(HandleExecutable):

    def validate(self, agent: Agent, signal: Signal) -> bool:
        return True

    def run(self, agent: Agent, signal: ChatTMR):
        tmr = SpeechTMR.build("I heard %s say '%s'." % (signal.agent().id, signal.raw_text()))
        agent.speak(tmr, join=True)
