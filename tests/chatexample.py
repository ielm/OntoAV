from ontoagent.engine.executable import HandleExecutable
from ontoagent.engine.signal import Signal
from ontocraft.agent import MalmoAgent
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.observers.chat import ChatTMR
from ontocraft.utils.MalmoUtils import bootstrap_specific
from ontograph.Frame import Frame
from ontocraft.observers.position import PositionXMR

from clagent.agent import CLAgent
from clagent.handle import ChatHandleExecutable

import time

if __name__ == '__main__':
    clients = [
        ("localhost", 10000),
        ("localhost", 10001),
    ]


    # Sasha, after the mission loads, will say "Hello world." one time.
    def bootstrap_sasha():
        agent_host = bootstrap_specific(("tests.resources", "25world.xml"), clients, 0)

        agent = CLAgent.build(agent_host,None)

        action = False
        while agent.host().getWorldState().is_mission_running:
            time.sleep(2)

            if not action:
                tmr = SpeechTMR.build("Hello world.")
                agent.speak(tmr, join=True)
                action = True


    # Jake, after the mission loads, will observer every 2 seconds.  When he finds a chat signal,
    # it will be analyzed and executed with the RespondToChatExecutable above (basically just printing a log).
    def bootstrap_jake():
        agent_host = bootstrap_specific(("tests.resources", "25world.xml"), clients, 1)

        agent = CLAgent.build(agent_host,None)

        # Jake needs to know who Sasha is, so the input signal can be attributed to the speaker correctly.
        sasha = Frame("@ENV.AGENT.?").add_parent("@ONT.AGENT")
        sasha["HAS-NAME"] = "Sasha"

        # Disable all of the other signal observations for optimization of this example.
        from ontocraft.observers.position import PositionSignal
        from ontocraft.observers.vision import SupervisionSignal
        # agent.disable_observer(PositionSignal)
        # agent.disable_observer(SupervisionSignal)

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
