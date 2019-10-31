from malmo.MalmoPython import AgentHost
from ontoagent.agent import Agent
from ontoagent.utils.analysis import Analyzer
from ontocraft.effectors.move import MoveAMR, MoveEffector
from ontocraft.observers.observer import MalmoObserver
from ontocraft.observers.position import PositionExecutable, PositionXMR
from ontograph.Frame import Frame


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

        # Define analyzers
        from ontocraft.observers.position import PositionAnalyzer
        from ontocraft.observers.vision import OcclusionVisionAnalyzer

        Analyzer.register_analyzer(PositionAnalyzer)
        Analyzer.register_analyzer(OcclusionVisionAnalyzer)

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
        MalmoObserver().observe(self, join=join)

    # Custom output overrides

    def move(self, amr: MoveAMR, join: bool=False):
        self.output(amr, self.move_effector(), join=join)

