from ontoagent.engine.effector import Effector
from ontoagent.engine.executable import EffectorExecutable
from ontoagent.engine.signal import TMR, XMR
from ontograph.Frame import Frame
from ontograph.Space import Space
from typing import Union

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ontocraft.agent import MalmoAgent


class SpeechTMR(TMR):

    @classmethod
    def build(cls, speech: str) -> 'SpeechTMR':
        anchor = Frame("@IO.TMR.?").add_parent(Frame("@ONT.TMR"))
        space = XMR.next_available_space("AMR")
        root = space.frame("@.SPEECH-ACT.?").add_parent("@ONT.SPEECH-ACT")

        root["AGENT"] = Frame("@SELF.AGENT.1")
        root["THEME"] = speech

        tmr = TMR.build(root, space=space, anchor=anchor)

        return SpeechTMR(tmr.anchor)

    def speech(self) -> str:
        return self.root()["THEME"].singleton()


class SpeechEffector(Effector):

    @classmethod
    def build(cls, space: Union[str, Space]=None) -> 'SpeechEffector':
        type = Frame("@ONT.SPEECH-EFFECTOR")
        effector = super().build(type=type, space=space, executable=SpeechEffectorExecutable)
        return SpeechEffector(effector.anchor)


class SpeechEffectorExecutable(EffectorExecutable):

    def run(self, agent: 'MalmoAgent', tmr: TMR, effector: Effector):
        if isinstance(tmr, SpeechTMR):
            speech = tmr.speech()
        else:
            speech = self.generate(tmr)

        agent.host().sendCommand("chat %s" % speech)

    def generate(self, tmr: TMR) -> str:
        return "Hello world."