from ontoagent.agent import Agent
from ontoagent.engine.executable import ProactiveExecutable
from ontoagent.engine.signal import Signal
from ontoagent.utils.common import AnchoredObject
from ontograph.Frame import Frame
from typing import List, Set, Type

import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ontocraft.agent import MalmoAgent


class MalmoObserver(AnchoredObject):

    @classmethod
    def build(cls, signal_type: Type[Signal], observation_fields: Set[str], cache_key: str, latest_only: bool) -> 'MalmoObserver':
        anchor = Frame("@SYS.MALMO-OBSERVER.?").add_parent("@ONT.MALMO-OBSERVER")
        anchor["TYPE"] = signal_type
        anchor["CACHE-KEY"] = cache_key
        anchor["FIELDS"] = list(observation_fields)
        anchor["ENABLED"] = True
        anchor["LATEST-ONLY"] = latest_only

        return MalmoObserver(anchor)

    def type(self) -> Type[Signal]:
        return self.anchor["TYPE"].singleton()

    def key(self) -> str:
        return self.anchor["CACHE-KEY"].singleton()

    def fields(self) -> List[str]:
        return list(self.anchor["FIELDS"])

    def enable(self):
        self.anchor["ENABLED"] = True

    def disable(self):
        self.anchor["ENABLED"] = False

    def is_enabled(self) -> bool:
        return self.anchor["ENABLED"].singleton()

    def is_latest_only(self) -> bool:
        return self.anchor["LATEST-ONLY"].singleton()


class MalmoMasterObserver(object):

    MALMO_OBSERVATION_CACHE_FRAME = "@SYS.MALMO-OBSERVATION-CACHE"
    MALMO_OBSERVERS_COLLECTION_FRAME = "@SYS.MALMO-OBSERVERS-COLLECTION"

    def observers(self) -> List[MalmoObserver]:
        return list(Frame(MalmoMasterObserver.MALMO_OBSERVERS_COLLECTION_FRAME)["HAS-OBSERVER"])

    def enable_observer(self, signal_type: Type[Signal], observation_fields: Set[str], cache_key: str, latest_only: bool=True):
        observers = self.observers()

        for observer in observers:
            if observer.type() == signal_type:
                observer.enable()
                return

        observer = MalmoObserver.build(signal_type, observation_fields, cache_key, latest_only)
        Frame(MalmoMasterObserver.MALMO_OBSERVERS_COLLECTION_FRAME)["HAS-OBSERVER"] += observer

    def disable_observer(self, signal_type: Type[Signal]):
        observers = self.observers()

        for observer in observers:
            if observer.type() == signal_type:
                observer.disable()
                return

    def observe(self, agent: 'MalmoAgent', join: bool=False):
        host = agent.host()
        world_state = host.getWorldState()

        cache = Frame(MalmoMasterObserver.MALMO_OBSERVATION_CACHE_FRAME)
        observations = list(world_state.observations)

        for i, observation in enumerate(observations):
            timestamp = int(observation.timestamp.timestamp() * 1000)
            if "LAST-OBSERVATION" not in cache or cache["LAST-OBSERVATION"].singleton() < timestamp:
                cache["LAST-OBSERVATION"] = timestamp
                observation = json.loads(observation.text)

                for observer in self.observers():
                    if observer.is_enabled() and (not observer.is_latest_only() or i == len(observations) -1):
                        self.observe_if_different(observer, observation, agent, join)

    def observe_if_different(self, observer: MalmoObserver, observation: dict, agent: Agent, join: bool):
        cache = Frame(MalmoMasterObserver.MALMO_OBSERVATION_CACHE_FRAME)

        value = dict()
        for field in observer.fields():
            if field not in observation:
                return
            value[field] = observation[field]

        if cache[observer.key()] == value:
            return

        agent.input(observer.type().build(value), join=join)


class MalmoObserverProactiveExecutable(ProactiveExecutable):

    def run(self, agent: 'MalmoAgent'):
        MalmoObserver().observe(agent)

