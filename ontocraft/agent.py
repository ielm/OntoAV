from malmo.MalmoPython import AgentHost
from ontoagent.agent import Agent
from ontoagent.engine.signal import Signal, TMR
from ontoagent.utils.analysis import Analyzer
from ontocraft.effectors.move import MoveAMR, MoveEffector
from ontocraft.effectors.speech import SpeechEffector
from ontocraft.observers.observer import MalmoMasterObserver
from ontocraft.observers.position import PositionExecutable, PositionXMR
from ontograph.Frame import Frame
from typing import Set, Type


class MalmoAgent(Agent):

    CACHED_HOST: AgentHost = None

    @classmethod
    def build(cls, host: AgentHost) -> 'MalmoAgent':
        agent = super().build(identity=None, agenda=None, evergreens=None, proactivity=None, ontology_loader=None)
        agent = MalmoAgent(agent.anchor)

        # Load additional Malmo-specific knowledge
        agent.load_knowledge("ontocraft.resources", "malmo.knowledge")

        # Define effectors
        agent.set_move_effector(MoveEffector.build())
        agent.set_speech_effector(SpeechEffector.build())

        # Define observers
        from ontocraft.observers.chat import ChatSignal
        from ontocraft.observers.position import PositionSignal
        from ontocraft.observers.vision import SupervisionSignal

        agent.enable_observer(ChatSignal, {"Chat"}, "chat")
        agent.enable_observer(PositionSignal, {"XPos", "YPos", "ZPos", "Yaw"}, "position")
        agent.enable_observer(SupervisionSignal, {"supervision"}, "supervision")

        # Define analyzers
        from ontocraft.observers.chat import ChatAnalyzer
        from ontocraft.observers.position import PositionAnalyzer
        from ontocraft.observers.vision import OcclusionVisionAnalyzer

        Analyzer.register_analyzer(ChatAnalyzer)
        Analyzer.register_analyzer(PositionAnalyzer)
        Analyzer.register_analyzer(OcclusionVisionAnalyzer)

        # ... and specify the SupervisionAnalyzer range - this must match the contents of the XML definition
        OcclusionVisionAnalyzer.set_supervision_min(-2, -2, -2)
        OcclusionVisionAnalyzer.set_supervision_max(2, 2, 2)

        # For now, remove the default TextAnalyzer from the list of analyzers
        from ontoagent.utils.analysis import TextAnalyzer
        Frame("@SYS.ANALYZER-REGISTRY")["HAS-ANALYZER"] -= TextAnalyzer

        # Define responses
        agent.add_response(Frame("@ONT.MOTION-EVENT"), PositionExecutable)

        # Attach Malmo host
        agent.set_host(host)

        return agent

    def singletons(self) -> Frame:
        return Frame("@SYS.SINGLETONS")

    def set_host(self, host: AgentHost):
        MalmoAgent.CACHED_HOST = host

    def host(self) -> AgentHost:
        return MalmoAgent.CACHED_HOST

    def set_move_effector(self, effector: MoveEffector):
        self.add_effector(effector)
        self.singletons()["MOVE-EFFECTOR"] = effector

    def move_effector(self) -> MoveEffector:
        return self.singletons()["MOVE-EFFECTOR"].singleton()

    def set_speech_effector(self, effector: SpeechEffector):
        self.add_effector(effector)
        self.singletons()["SPEECH-EFFECTOR"] = effector

    def speech_effector(self) -> SpeechEffector:
        return self.singletons()["SPEECH-EFFECTOR"].singleton()

    def set_position(self, x: float, y: float, z: float, facing: PositionXMR.Facing):
        self.anchor["XPOS"] = x
        self.anchor["YPOS"] = y
        self.anchor["ZPOS"] = z
        self.anchor["FACING"] = facing

    def x(self) -> float:
        return self.anchor["XPOS"].singleton()

    def y(self) -> float:
        return self.anchor["YPOS"].singleton()

    def z(self) -> float:
        return self.anchor["ZPOS"].singleton()

    def facing(self) -> PositionXMR.Facing:
        return self.anchor["FACING"].singleton()

    # Custom input overrides

    def observe(self, join: bool=False):
        MalmoMasterObserver().observe(self, join=join)

    def enable_observer(self, signal_type: Type[Signal], observation_fields: Set[str], cache_key: str):
        MalmoMasterObserver().enable_observer(signal_type, observation_fields, cache_key)

    def disable_observer(self, signal_type: Type[Signal]):
        MalmoMasterObserver().disable_observer(signal_type)

    # Custom output overrides

    def move(self, amr: MoveAMR, join: bool=False):
        self.output(amr, self.move_effector(), join=join)

    def speak(self, tmr: TMR, join: bool=False):
        self.output(tmr, self.speech_effector(), join=join)

