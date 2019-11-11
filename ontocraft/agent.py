from malmo import MalmoPython
from ontoagent.agent import Agent
from ontoagent.engine.signal import Signal, TMR
from ontoagent.utils.analysis import Analyzer
from ontocraft.effectors.move import MoveAMR, MoveEffector
from ontocraft.effectors.speech import SpeechEffector
from ontocraft.observers.observer import MalmoMasterObserver
from ontocraft.observers.position import PositionExecutable, PositionXMR
from ontocraft.utils.MalmoUtils import OntoCraftAgentHost
from ontograph.Frame import Frame
from typing import Set, Type

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ontocraft.views.environment import MalmoEnvironment


class MalmoAgent(Agent):

    CACHED_HOST: OntoCraftAgentHost = None

    @classmethod
    def build(cls, host: OntoCraftAgentHost) -> 'MalmoAgent':
        agent = super().build(identity=None, agenda=None, evergreens=None, proactivity=None, ontology_loader=None)
        agent = MalmoAgent(agent.anchor)
        agent.anchor["HAS-NAME"] = host.name()

        from ontocraft.views.environment import MalmoEnvironment
        agent.anchor["HAS-ENVIRONMENT"] = MalmoEnvironment.build()

        # Load additional Malmo-specific knowledge
        agent.load_knowledge("ontocraft.resources", "malmo.knowledge")

        # Define effectors
        if host.discrete_movement():
            agent.set_move_effector(MoveEffector.build())

        if host.chat()[1]:
            agent.set_speech_effector(SpeechEffector.build())

        # Define observers, analyzers, and responses
        if host.chat()[0]:
            host.setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

            from ontocraft.observers.chat import ChatSignal
            agent.enable_observer(ChatSignal, {"Chat"}, "chat", latest_only=False)

            from ontocraft.observers.chat import ChatAnalyzer
            Analyzer.register_analyzer(ChatAnalyzer)

        if host.position():
            from ontocraft.observers.position import PositionSignal
            agent.enable_observer(PositionSignal, {"XPos", "YPos", "ZPos", "Yaw"}, "position")

            from ontocraft.observers.position import PositionAnalyzer
            Analyzer.register_analyzer(PositionAnalyzer)

            agent.add_response(Frame("@ONT.MOTION-EVENT"), PositionExecutable)

        if host.supervision() is not None:
            from ontocraft.observers.vision import SupervisionSignal
            agent.enable_observer(SupervisionSignal, {"supervision"}, "supervision")

            from ontocraft.observers.vision import OcclusionVisionAnalyzer
            Analyzer.register_analyzer(OcclusionVisionAnalyzer)

            supervision = host.supervision()
            OcclusionVisionAnalyzer.set_supervision_min(*list(supervision[0]))
            OcclusionVisionAnalyzer.set_supervision_max(*list(supervision[1]))

            from ontocraft.observers.vision import SupervisionExecutable
            agent.add_response(Frame("@ONT.VISUAL-EVENT"), SupervisionExecutable)

        # For now, remove the default TextAnalyzer from the list of analyzers
        from ontoagent.utils.analysis import TextAnalyzer
        Frame("@SYS.ANALYZER-REGISTRY")["HAS-ANALYZER"] -= TextAnalyzer

        # Attach Malmo host
        agent.set_host(host)

        return agent

    def singletons(self) -> Frame:
        return Frame("@SYS.SINGLETONS")

    def set_host(self, host: OntoCraftAgentHost):
        MalmoAgent.CACHED_HOST = host

    def host(self) -> OntoCraftAgentHost:
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

    def environment(self) -> 'MalmoEnvironment':
        return self.anchor["HAS-ENVIRONMENT"].singleton()

    # Custom input overrides

    def observe(self, join: bool=False):
        MalmoMasterObserver().observe(self, join=join)

    def enable_observer(self, signal_type: Type[Signal], observation_fields: Set[str], cache_key: str, latest_only: bool=True):
        MalmoMasterObserver().enable_observer(signal_type, observation_fields, cache_key, latest_only=latest_only)

    def disable_observer(self, signal_type: Type[Signal]):
        MalmoMasterObserver().disable_observer(signal_type)

    # Custom output overrides

    def move(self, amr: MoveAMR, join: bool=False):
        self.output(amr, self.move_effector(), join=join)

    def speak(self, tmr: TMR, join: bool=False):
        self.output(tmr, self.speech_effector(), join=join)

