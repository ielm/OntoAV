from enum import Enum
from malmo.MalmoPython import WorldState
from ontoagent.agent import Agent
from ontoagent.engine.executable import HandleExecutable
from ontoagent.engine.signal import Signal, XMR
from ontoagent.utils.analysis import Analyzer
from ontograph.Frame import Frame

import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ontocraft.agent import MalmoAgent


class PositionSignal(Signal):

    @classmethod
    def build(cls, worldstate: WorldState) -> 'PositionSignal':
        anchor = Frame("@IO.XMR.?").add_parent("@ONT.XMR")
        space = XMR.next_available_space("XMR")

        root = space.frame("@.MOTION-EVENT.?").add_parent("@ONT.MOTION-EVENT")
        theme = space.frame("@.MALMO-POSITION.?").add_parent("@ONT.MALMO-POSITION")

        root["THEME"] = theme

        observations = json.loads(worldstate.observations[0].text)
        theme["XPOS"] = observations["XPos"]
        theme["YPOS"] = observations["YPos"]
        theme["ZPOS"] = observations["ZPos"]
        theme["YAW"] = observations["Yaw"]

        constituents = [root, theme]

        signal = super().build(root, space=space, anchor=anchor, constituents=constituents)
        return PositionSignal(signal.anchor)

    def xpos(self) -> float:
        return self.root()["THEME"].singleton()["XPOS"].singleton()

    def ypos(self) -> float:
        return self.root()["THEME"].singleton()["YPOS"].singleton()

    def zpos(self) -> float:
        return self.root()["THEME"].singleton()["ZPOS"].singleton()

    def yaw(self) -> float:
        return self.root()["THEME"].singleton()["YAW"].singleton()


class PositionXMR(XMR):

    class Facing(Enum):
        NORTH   = "NORTH"
        SOUTH   = "SOUTH"
        EAST    = "EAST"
        WEST    = "WEST"

    @classmethod
    def build(cls, x: float, y: float, z: float, facing: Facing) -> 'PositionXMR':
        anchor = Frame("@IO.XMR.?").add_parent("@ONT.XMR")
        space = XMR.next_available_space("XMR")
        root = space.frame("@.MOTION-EVENT.?").add_parent("@ONT.MOTION-EVENT")
        theme = space.frame("@.MALMO-POSITION.?").add_parent("@ONT.MALMO-POSITION")

        root["THEME"] = theme

        constituents = [theme]

        s = super().build(root, space=space, anchor=anchor, constituents=constituents)
        xmr = PositionXMR(s.anchor)

        xmr.set_x(x)
        xmr.set_y(y)
        xmr.set_z(z)
        xmr.set_facing(facing)

        return xmr

    def x(self) -> float:
        return self.root()["THEME"].singleton()["X"].singleton()

    def set_x(self, x: float):
        self.root()["THEME"].singleton()["X"] = x

    def y(self) -> float:
        return self.root()["THEME"].singleton()["Y"].singleton()

    def set_y(self, y: float):
        self.root()["THEME"].singleton()["Y"] = y

    def z(self) -> float:
        return self.root()["THEME"].singleton()["Z"].singleton()

    def set_z(self, z: float):
        self.root()["THEME"].singleton()["Z"] = z

    def facing(self) -> Facing:
        return self.root()["THEME"].singleton()["FACING"].singleton()

    def set_facing(self, facing: Facing):
        self.root()["THEME"].singleton()["FACING"] = facing


class PositionAnalyzer(Analyzer):

    def __init__(self):
        super().__init__()

        self.header = "XMR"
        self.root_property = "XMR-ROOT"
        self.xmr_type = PositionXMR

    def is_appropriate(self, signal: Signal) -> bool:
        root = signal.root()
        return root ^ Frame("@ONT.MOTION-EVENT") and root["THEME"].singleton() ^ Frame("@ONT.MALMO-POSITION")

    def to_signal(self, input: PositionSignal) -> PositionXMR:
        facing = {
            0.0: PositionXMR.Facing.SOUTH,
            90.0: PositionXMR.Facing.WEST,
            180.0: PositionXMR.Facing.NORTH,
            270.0: PositionXMR.Facing.EAST
        }[input.yaw()]

        xmr = PositionXMR.build(input.xpos(), input.ypos(), input.zpos(), facing)
        return xmr


class PositionExecutable(HandleExecutable):

    def validate(self, agent: 'MalmoAgent', signal: Signal) -> bool:
        return signal.root() ^ Frame("@ONT.MOTION-EVENT") and signal.root()["THEME"].singleton() ^ Frame("@ONT.MALMO-POSITION")

    def run(self, agent: 'MalmoAgent', signal: PositionXMR):
        agent.set_position(signal.x(), signal.y(), signal.z(), signal.facing())