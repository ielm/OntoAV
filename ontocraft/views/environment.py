from ontoagent.utils.common import AnchoredObject
from ontocraft.observers.vision import MalmoBlock, MalmoVMR
from ontograph.Frame import Frame
from ontograph.Query import Query
from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ontocraft.agent import MalmoAgent


class MalmoBlockOverTime(MalmoBlock):

    @classmethod
    def build(cls, x: int, y: int, z: int) -> 'MalmoBlockOverTime':
        frame = Frame("@ENV.MALMO-BLOCK.?").add_parent("@ONT.MALMO-BLOCK")
        b = MalmoBlockOverTime(frame)
        b.set_type("")
        b.set_absx(x)
        b.set_absy(y)
        b.set_absz(z)

        return b

    def add_observation(self, block: 'MalmoBlock'):
        self.anchor["HAS-OBSERVATION"] += block

    def observations(self) -> List['MalmoBlock']:
        return list(self.anchor["HAS-OBSERVATION"])

    def type(self) -> str:
        observations = self.observations()
        if len(observations) > 0:
            return observations[-1].type()
        return super().type()


class MalmoEnvironment(AnchoredObject):

    @classmethod
    def build(cls) -> 'MalmoEnvironment':
        frame = Frame("@ENV.ENVIRONMENT.?").add_parent("@ONT.ENVIRONMENT")

        return MalmoEnvironment(frame)

    def update(self, agent: 'MalmoAgent', vmr: 'MalmoVMR'):
        blocks = vmr.blocks()

        for block in blocks:
            block_over_time = self.block(block.absx(), block.absy(), block.absz())
            if block_over_time.type() != block.type():
                block_over_time.add_observation(block)

    def block(self, absx: int, absy: int, absz: int) -> MalmoBlockOverTime:
        query = Query(
            Query.AND(
                Query.inspace("ENV"),
                Query.exists(slot="ABSX", filler=absx, local=True),
                Query.exists(slot="ABSY", filler=absy, local=True),
                Query.exists(slot="ABSZ", filler=absz, local=True),
            )
        )

        results = list(query.start())
        if len(results) == 1:
            return MalmoBlockOverTime(results[0])

        block = MalmoBlockOverTime.build(absx, absy, absz)
        self.add_block(block)

        return block

    def relative_block(self, agent: 'MalmoAgent', relx: int, rely: int, relz: int) -> MalmoBlockOverTime:
        absx = relx + int(agent.x())
        absy = rely + int(agent.y())
        absz = relz + int(agent.z())

        return self.block(absx, absy, absz)

    def blocks(self) -> List[MalmoBlockOverTime]:
        return list(self.anchor["HAS-BLOCK"])

    def add_block(self, block: MalmoBlockOverTime):
        self.anchor["HAS-BLOCK"] += block