from ontoagent.agent import Agent
from ontoagent.engine.executable import HandleExecutable
from ontoagent.engine.signal import Signal, XMR
from ontograph.Frame import Frame
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.observers.chat import ChatTMR
from clagent.agent import CLAgent


class CommandHandleExecutable(HandleExecutable):

    def validate(self, agent: CLAgent, signal: Signal) -> bool:
        return signal.root() ^ Frame("@ONT.SPEECH-ACT") and signal.root()["THEME"].singleton() ^ Frame("@ONT.RAW-TEXT") and signal.agent().id == "@ENV.AGENT.1"

    def run(self, agent: CLAgent, signal: ChatTMR):
        text = signal.raw_text()
        path = None
        if self.is_pretentious(text):
            tmr = SpeechTMR.build("Nothing beside remains. Round the decay Of that colossal wreck, boundless and bare The lone and level sands stretch far away.")
        elif self.is_command(text):
            path, tmr = self.parse_command(text)
        else:
            tmr = SpeechTMR.build("I heard %s say '%s'." % (signal.agent().id, text))
        agent.speak(tmr, join=True)
        if path is not None:
            agent.movepath(path)

    @staticmethod
    def is_pretentious(signal: str) -> bool:
        if signal == "My name is Ozymandias, king of agents: Look on my works, ye Mighty, and despair!":
            return True
        else:
            return False

    @staticmethod
    def is_command(signal: str) -> bool:
        if True in list(map(lambda c: c in signal.lower(), ["move", "walk", "turn", "go"])):
            return True
        else:
            return False

    @staticmethod
    def parse_command(signal: str):
        command = signal.lower()

        def _get_digits(text):
            return ''.join(filter(lambda x: x.isdigit(), text))

        if "move" in command:
            if "forward" in command:
                digit = _get_digits(command)
                digit = "1" if digit == "" else digit
                path = "fx" + digit
                return path, SpeechTMR.build("Moving forward %s step(s)" % digit)
            if "backward" in command:
                digit = _get_digits(command)
                digit = "1" if digit == "" else digit
                path = "bx" + digit
                return path, SpeechTMR.build("Moving backward %s step(s)" % digit)

        if "turn" in command:
            if True in list(map(lambda c: c in command, ["right", "clockwise", "cw"])):
                digit = _get_digits(command)

                digit = "1" if digit == "" else digit
                path = "cwx" + digit
                return path, SpeechTMR.build("Turning clockwise %s step(s)" % digit)
            if True in list(map(lambda c: c in command, ["left", "counterclockwise", "ccw"])):
                digit = _get_digits(command)
                digit = "1" if digit == "" else digit
                path = "ccwx" + digit
                return path, SpeechTMR.build("Turning counter-clockwise %s step(s)" % digit)
