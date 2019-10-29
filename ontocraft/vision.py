from malmo.MalmoPython import WorldState
from ontoagent.agent import Agent
from ontoagent.engine.signal import Signal, XMR
from ontoagent.utils.analysis import Analyzer
from ontoagent.utils.common import AnchoredObject
from ontograph.Frame import Frame
from typing import Iterable, List, Tuple, Union

import itertools
import math
import numpy as np
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

    class Block(object):

        def __init__(self, block_dict: dict, relative_position: Tuple[float, float, float]):
            self.original_dict = block_dict

            # Potentially fractional numbers
            self.observed_x = block_dict["coords"][0] + relative_position[0]
            self.observed_y = block_dict["coords"][1] + relative_position[1]
            self.observed_z = block_dict["coords"][2] + relative_position[2]

            # Calculate bounds
            self.min_x = math.floor(self.observed_x)
            self.max_x = self.min_x + 1 if self.min_x >= 0 else self.min_x - 1

            self.min_y = math.floor(self.observed_y)
            self.max_y = self.min_y + 1 if self.min_y >= 0 else self.min_y - 1

            self.min_z = math.floor(self.observed_z)
            self.max_z = self.min_z + 1 if self.min_z >= 0 else self.min_z - 1

            # Calculate the planes
            self.planes = [
                LanternAnalyzer.Plane(
                    (self.min_x, self.max_y, self.max_z),
                    (self.max_x, self.max_y, self.max_z),
                    (self.max_x, self.max_y, self.min_z)),  # Top
                LanternAnalyzer.Plane(
                    (self.min_x, self.min_y, self.max_z),
                    (self.max_x, self.min_y, self.max_z),
                    (self.max_x, self.min_y, self.min_z)),  # Bottom
                LanternAnalyzer.Plane(
                    (self.min_x, self.max_y, self.min_z),
                    (self.max_x, self.max_y, self.min_z),
                    (self.max_x, self.min_y, self.min_z)),  # Front
                LanternAnalyzer.Plane(
                    (self.min_x, self.max_y, self.max_z),
                    (self.max_x, self.max_y, self.max_z),
                    (self.max_x, self.min_y, self.max_z)),  # Back
                LanternAnalyzer.Plane(
                    (self.min_x, self.max_y, self.max_z),
                    (self.min_x, self.min_y, self.max_z),
                    (self.min_x, self.min_y, self.min_z)),  # Left
                LanternAnalyzer.Plane(
                    (self.max_x, self.max_y, self.max_z),
                    (self.max_x, self.min_y, self.max_z),
                    (self.max_x, self.min_y, self.min_z)),  # Right
            ]

        def center(self) -> Tuple[float, float, float]:
            return self.min_x + 0.5, self.min_y + 0.5, self.min_z + 0.5

        def surface_centers(self) -> List[Tuple[float, float, float]]:
            return [
                (self.min_x + 0.5, self.max_y, self.min_z + 0.5),   # Top
                (self.min_x + 0.5, self.min_y, self.min_z + 0.5),   # Bottom
                (self.min_x + 0.5, self.min_y + 0.5, self.min_z),   # Front
                (self.min_x + 0.5, self.min_y + 0.5, self.max_z),   # Back
                (self.min_x, self.min_y + 0.5, self.min_z + 0.5),   # Left
                (self.max_x, self.min_y + 0.5, self.min_z + 0.5),   # Right
            ]

        def is_point_on_surface(self, point: Tuple[float, float, float]) -> bool:
            # Does it lie on the top?
            if point[1] == self.max_y and (self.min_x <= point[0] <= self.max_x) and (self.min_z <= point[2] <= self.max_z):
                return True
            # Does it lie on the bottom?
            if point[1] == self.min_y and (self.min_x <= point[0] <= self.max_x) and (self.min_z <= point[2] <= self.max_z):
                return True
            # Does it lie on the front?
            if point[2] == self.min_z and (self.min_x <= point[0] <= self.max_x) and (self.min_y <= point[1] <= self.max_y):
                return True
            # Does it lie on the back?
            if point[2] == self.max_z and (self.min_x <= point[0] <= self.max_x) and (self.min_y <= point[1] <= self.max_y):
                return True
            # Does it lie on the left?
            if point[0] == self.min_x and (self.min_y <= point[1] <= self.max_y) and (self.min_z <= point[2] <= self.max_z):
                return True
            # Does it lie on the right?
            if point[0] == self.max_x and (self.min_y <= point[1] <= self.max_y) and (self.min_z <= point[2] <= self.max_z):
                return True

            return False

        def __eq__(self, other):
            if isinstance(other, LanternAnalyzer.Block):
                return self.observed_x == other.observed_x and self.observed_y == other.observed_y and self.observed_z == other.observed_z
            return super().__eq__(other)

    class Plane(object):

        def __init__(self, p1: Tuple[float, float, float], p2: Tuple[float, float, float],
                     p3: Tuple[float, float, float]):
            self.v1 = np.array(list(p1))
            self.v2 = np.array(list(p2))
            self.v3 = np.array(list(p3))
            self.normal = np.cross((self.v2 - self.v1), (self.v3 - self.v1))

        def does_segment_intersect(self, start: np.ndarray, end: np.ndarray) -> bool:
            plane_point = self.v1
            plane_normal = self.normal

            start_side = np.dot(start - plane_point, plane_normal)
            end_side = np.dot(end - plane_point, plane_normal)

            diff = start_side * end_side

            return diff <= 0

        def point_of_intersection(self, start: np.ndarray, end: np.ndarray, epsilon=1e-6) -> Union[None, Tuple[float, float, float]]:
            plane_point = self.v1
            plane_normal = self.normal

            u = end - start
            dot = np.dot(plane_normal, u)

            if abs(dot) > epsilon:
                w = start - plane_point
                fac = -np.dot(plane_normal, w) / dot
                u = u * fac
                return tuple(start + u)
            else:
                # The segment is parallel to the plane
                return None

    def filter_blocks(self, blocks: Iterable[dict]) -> Iterable[dict]:
        blocks = list(super().filter_blocks(blocks))

        agent = Agent(Frame("@SELF.AGENT.1"))
        rel_x = agent.anchor["XPOS"].singleton()
        rel_y = agent.anchor["YPOS"].singleton()
        rel_z = agent.anchor["ZPOS"].singleton()

        relative_position = (rel_x, rel_y, rel_z)

        eyes = (rel_x, rel_y + 0.5, rel_z)
        eyes = np.array(list(eyes))

        _blocks = list(map(lambda block: LanternAnalyzer.Block(block, relative_position), blocks))
        filtered = list(filter(lambda block: not self.is_block_occluded(block, _blocks, eyes), _blocks))

        return map(lambda block: block.original_dict, filtered)

    def is_block_occluded(self, block: Block, blocks: List[Block], eyes: np.ndarray) -> bool:
        centers = block.surface_centers()
        relative_x = block.original_dict["coords"][0]
        relative_y = block.original_dict["coords"][1]
        relative_z = block.original_dict["coords"][2]

        def is_face_occluded(center: Tuple[float, float, float]) -> bool:
            center = np.array(list(center))

            for candidate in blocks:
                if candidate == block:
                    continue
                if candidate.original_dict["coords"][0] * relative_x == -1:
                    continue
                if candidate.original_dict["coords"][1] * relative_y == -1:
                    continue
                if candidate.original_dict["coords"][2] * relative_z == -1:
                    continue

                for plane in candidate.planes:
                    if plane.does_segment_intersect(eyes, center):
                        point = plane.point_of_intersection(eyes, center)
                        if candidate.is_point_on_surface(point):
                            return True

            return False

        for center in centers:
            if not is_face_occluded(center):
                return False

        return True


# FlashlightAnalyzer is a LanternAnalyzer that respects facing information of the agent.
class FlashlightAnalyzer(LanternAnalyzer):
    pass