from malmo.MalmoPython import WorldState
from ontoagent.agent import Agent
from ontoagent.engine.executable import ProactiveExecutable
from ontoagent.engine.signal import Signal
from ontocraft.observers.position import PositionSignal
from ontocraft.observers.vision import SupervisionSignal
from ontograph.Frame import Frame
from typing import Set, Type

import json


class MalmoObserver(object):

    MALMO_OBSERVATION_CACHE_FRAME = "@SYS.MALMO-OBSERVATION-CACHE"

    def observe(self, agent: Agent, join: bool=False):
        host = Agent.malmo_host
        world_state = host.getWorldState()

        self.observe_if_different("position", {"XPos", "YPos", "ZPos", "Yaw"}, world_state, PositionSignal, agent, join)
        self.observe_if_different("supervision", {"supervision5x5"}, world_state, SupervisionSignal, agent, join)

    def observe_if_different(self, key: str, fields: Set[str], world_state: WorldState, signal_type: Type[Signal], agent: Agent, join: bool):
        cache = Frame(MalmoObserver.MALMO_OBSERVATION_CACHE_FRAME)
        observations = json.loads(world_state.observations[0].text)

        value = dict()
        for field in fields:
            value[field] = observations[field]

        if cache[key] == value:
            return

        cache[key] = value

        agent.input(signal_type.build(world_state), join=join)


class MalmoObserverProactiveExecutable(ProactiveExecutable):

    def run(self, agent: Agent):
        MalmoObserver().observe(agent)

