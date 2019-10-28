from malmo.MalmoPython import WorldState
from ontoagent.agent import Agent
from ontoagent.engine.signal import Signal, XMR
from ontoagent.utils.analysis import Analyzer
from ontoagent.utils.common import AnchoredObject
from ontograph.Frame import Frame
from typing import Iterable, List

import math
import json


class SupervisionSignal(Signal):

    @classmethod
    def build(cls, worldstate: WorldState) -> 'SupervisionSignal':
        anchor = Frame("@IO.VMR.?").add_parent("@ONT.VMR")
        space = XMR.next_available_space("VMR")

        root = space.frame("@.VISUAL-EVENT.?").add_parent("@ONT.VISUAL-EVENT")
        theme = space.frame("@.MALMO-OBSERVATION-GRID.?").add_parent("@ONT.MALMO-OBSERVATION-GRID")

        root["THEME"] = theme

        supervision = json.loads(worldstate.observations[0].text)["supervision5x5"]
        supervision = ";".join(supervision)
        theme["VALUE"] = supervision

        constituents = [root, theme]

        signal = super().build(root, space=space, anchor=anchor, constituents=constituents)
        return SupervisionSignal(signal.anchor)

    def raw_grid(self) -> List[str]:
        return self.root()["THEME"].singleton()["VALUE"].singleton().split(";")


class MalmoBlock(AnchoredObject):

    @classmethod
    def build(cls, type: str, absx: int, absy: int, absz: int) -> 'MalmoBlock':
        frame = Frame("@ENV.MALMO-BLOCK.?").add_parent("@ONT.MALMO-BLOCK")
        b = MalmoBlock(frame)
        b.set_type(type)
        b.set_absx(absx)
        b.set_absy(absy)
        b.set_absz(absz)

        return b

    def type(self) -> str:
        return self.anchor["TYPE"].singleton()

    def set_type(self, type: str):
        self.anchor["TYPE"] = type

    def absx(self) -> int:
        return self.anchor["ABSX"].singleton()

    def set_absx(self, absx: int):
        self.anchor["ABSX"] = absx

    def absy(self) -> int:
        return self.anchor["ABSY"].singleton()

    def set_absy(self, absy: int):
        self.anchor["ABSY"] = absy

    def absz(self) -> int:
        return self.anchor["ABSZ"].singleton()

    def set_absz(self, absz: int):
        self.anchor["ABSZ"] = absz


class MalmoVMR(XMR):

    @classmethod
    def build(cls, blocks: List[MalmoBlock]) -> 'MalmoVMR':
        anchor = Frame("@IO.VMR.?").add_parent("@ONT.VMR")
        space = XMR.next_available_space("VMR")
        root = space.frame("@.VISUAL-EVENT.?").add_parent("@ONT.VISUAL-EVENT")
        constituents = list(map(lambda block: block.anchor, blocks))

        s = super().build(root, space=space, anchor=anchor, constituents=constituents)
        v = MalmoVMR(s.anchor)

        v.set_blocks(blocks)

        return v

    def blocks(self) -> List[MalmoBlock]:
        return self.root()["THEME"]

    def set_blocks(self, blocks: List[MalmoBlock]):
        self.root()["THEME"] = blocks


# A SupervisionAnalyzer can see all blocks in the supplied malmo observation grid.
# Solid blocks do not occlude blocks behind them.
# Facing information of the agent is not respected.
class SupervisionAnalyzer(Analyzer):

    def __init__(self):
        super().__init__()

        self.header = "VMR"
        self.root_property = "VMR-ROOT"
        self.xmr_type = MalmoVMR

    def is_appropriate(self, signal: Signal) -> bool:
        root = signal.root()
        return root ^ Frame("@ONT.VISUAL-EVENT") and root["THEME"].singleton() ^ Frame("@ONT.MALMO-OBSERVATION-GRID")

    def to_signal(self, input: SupervisionSignal) -> MalmoVMR:
        size = len(input.raw_grid())
        cube = int(math.pow(size, 1/3))
        indexes = list(range(-int(cube/2), int(cube/2) + 1))

        block_stream = iter(input.raw_grid())
        blocks = []

        for y in indexes:
            for z in indexes:
                for x in indexes:
                    blocks.append({
                        "type": next(block_stream),
                        "coords": (x, y, z)
                    })

        blocks = self.filter_blocks(blocks)

        agent = Agent(Frame("@SELF.AGENT.1"))
        abs_x = int(agent.anchor["XPOS"].singleton())
        abs_y = int(agent.anchor["YPOS"].singleton())
        abs_z = int(agent.anchor["ZPOS"].singleton())
        blocks = map(lambda block: MalmoBlock.build(block["type"], block["coords"][0] + abs_x, block["coords"][1] + abs_y, block["coords"][2] + abs_z), blocks)

        blocks = list(blocks)
        print("Writing %d blocks" % len(blocks))

        return MalmoVMR.build(blocks)

    def filter_blocks(self, blocks: Iterable[dict]) -> Iterable[dict]:
        return filter(lambda block: block["type"] != "air", blocks)


# LanternAnalyzer is a SupervisionAnalyzer that respects solid block occlusion.
# Facing information of the agent is not respected.
class LanternAnalyzer(SupervisionAnalyzer):
    pass


# FlashlightAnalyzer is a LanternAnalyzer that respects facing information of the agent.
class FlashlightAnalyzer(LanternAnalyzer):
    pass