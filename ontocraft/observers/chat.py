from ontoagent.engine.signal import Signal, XMR
from ontoagent.utils.analysis import Analyzer
from ontograph.Frame import Frame
from ontograph.Query import Query


class ChatSignal(Signal):

    @classmethod
    def build(cls, observation: dict) -> 'ChatSignal':
        anchor = Frame("@IO.XMR.?").add_parent("@ONT.XMR")
        space = XMR.next_available_space("XMR")

        root = space.frame("@.SPEECH-ACT.?").add_parent("@ONT.SPEECH-ACT")
        theme = space.frame("@.RAW-TEXT.?").add_parent("@ONT.RAW-TEXT")

        root["THEME"] = theme

        chat = observation["Chat"][0]
        content = chat[chat.index(">") + 1:].strip()
        agent_name = chat[1:chat.index(">")]

        agent = None

        q = Query(Query.AND(Query.inspace("ENV"), Query.isa("@ONT.AGENT")))
        for candidate in q.start():
            if candidate["HAS-NAME"] == agent_name:
                agent = candidate
                break

        theme["VALUE"] = content
        root["AGENT"] = agent

        constituents = [root, theme]

        signal = super().build(root, space=space, anchor=anchor, constituents=constituents)
        return ChatSignal(signal.anchor)

    def raw_text(self) -> str:
        return self.root()["THEME"].singleton()["VALUE"].singleton()

    def agent(self) -> Frame:
        return self.root()["AGENT"].singleton()


class ChatTMR(XMR):

    # This is a placeholder that is effectively a clone of the input ChatSignal, see below.

    @classmethod
    def build(cls, signal: ChatSignal) -> 'ChatTMR':
        anchor = Frame("@IO.TMR.?").add_parent("@ONT.TMR")
        space = XMR.next_available_space("TMR")

        root = space.frame("@.SPEECH-ACT.?").add_parent("@ONT.SPEECH-ACT")
        theme = space.frame("@.RAW-TEXT.?").add_parent("@ONT.RAW-TEXT")

        root["THEME"] = theme

        theme["VALUE"] = signal.raw_text()
        root["AGENT"] = signal.agent()

        constituents = [root, theme]

        signal = super().build(root, space=space, anchor=anchor, constituents=constituents)
        return ChatTMR(signal.anchor)

    def raw_text(self) -> str:
        return self.root()["THEME"].singleton()["VALUE"].singleton()

    def agent(self) -> Frame:
        return self.root()["AGENT"].singleton()


class ChatAnalyzer(Analyzer):

    # This is a placeholder for using the real text analyzer; no analysis occurs, the ChatSignal
    # is just converted into a ChatTMR.

    def __init__(self):
        super().__init__()

        self.header = "TMR"
        self.root_property = "TMR-ROOT"
        self.xmr_type = ChatTMR

    def is_appropriate(self, signal: Signal) -> bool:
        root = signal.root()
        return root ^ Frame("@ONT.SPEECH-ACT") and root["THEME"].singleton() ^ Frame("@ONT.RAW-TEXT")

    def to_signal(self, input: ChatSignal) -> ChatTMR:
        return ChatTMR.build(input)
