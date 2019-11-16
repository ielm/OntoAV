from ontoagent.engine.executable import HandleExecutable
from ontoagent.engine.signal import Signal
from ontocraft.agent import MalmoAgent
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.observers.chat import ChatTMR
from ontocraft.utils.MalmoUtils import bootstrap_specific
from ontograph.Frame import Frame

from clagent.agent import CLAgent
from clagent.handle import ChatHandleExecutable

import time

if __name__ == '__main__':
    clients = [
        ("localhost", 10000),
        ("localhost", 10001),
    ]

    def bootstrap_sasha():
        agent_host = bootstrap_specific(("resources", "25world.xml"), clients, 0)

        agent = CLAgent.build(agent_host)

        action = False
        while agent.host().getWorldState().is_mission_running:
            time.sleep(3)

            if not action:
                tmr = SpeechTMR.build("Hello world.")
                agent.speak(tmr, join=True)
                action = True

    # Jake, after the mission loads, will observe every 2 seconds.  When he finds a chat signal,
    # it will be analyzed and execute a chat handler which checks for movement commands. On
    # a movement command, Jake will execute the movement command.
    def bootstrap_jake():
        agent_host = bootstrap_specific(("resources", "25world.xml"), clients, 1)

        agent = CLAgent.build(agent_host)

        # Jake needs to know who Sasha is, so the input signal can be attributed to the speaker correctly.
        sasha = Frame("@ENV.AGENT.?").add_parent("@ONT.AGENT")
        sasha["HAS-NAME"] = "Sasha"

        # Make sure Jake knows how to respond to an analyzed speech act.
        agent.add_response(Frame("@ONT.SPEECH-ACT"), ChatHandleExecutable)

        while agent.host().getWorldState().is_mission_running:
            time.sleep(2)

            agent.observe(join=True)

    # Make a process for bootstrapping and running each agent; they do not need to be joined or timed otherwise.
    from multiprocessing import Process

    p1 = Process(target=bootstrap_sasha)
    p1.start()

    p2 = Process(target=bootstrap_jake)
    p2.start()
