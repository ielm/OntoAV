from ontoagent.engine.executable import HandleExecutable
from ontoagent.engine.signal import Signal
from ontocraft.agent import MalmoAgent
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.observers.chat import ChatTMR
from ontocraft.utils.MalmoUtils import bootstrap_specific
from ontograph.Frame import Frame

from clagent.agent import CLAgent

import time

if __name__ == '__main__':
    clients = [
        ("localhost", 10000),
        ("localhost", 10001),
    ]

    map_file = ("worldtest.resources", "map.txt")
    world_file = ("worldtest.resources", "storyboard.xml")

    def bootstrap_agent():
        agent_host = bootstrap_specific(world_file, clients, 0)

        agent = CLAgent.build(agent_host, map_file)

        while agent.host().getWorldState().is_mission_running:
            time.sleep(1)
            agent.observe(join=True)


    def bootstrap_human():
        agent_host = bootstrap_specific(world_file, clients, 1)

        agent = MalmoAgent.build(agent_host)

        time.sleep(3)
        agent.speak(SpeechTMR.build("Go to the grocery store."), join=True)
        time.sleep(14)
        agent.speak(SpeechTMR.build("Actually, go to the pharmacy first."), join=True)

        while agent.host().getWorldState().is_mission_running:
            time.sleep(2)

    from multiprocessing import Process

    p1 = Process(target=bootstrap_agent)
    p1.start()

    p2 = Process(target=bootstrap_human)
    p2.start()
