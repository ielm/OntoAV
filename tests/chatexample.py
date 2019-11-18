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

    def bootstrap_user():
        agent_host = bootstrap_specific(("resources", "25world.xml"), clients, 0)

        user = CLAgent.build(agent_host)

        action = False
        while user.host().getWorldState().is_mission_running:
            time.sleep(2)

            if not action:
                tmr = SpeechTMR.build("Hello world.")
                user.speak(tmr, join=True)
                action = True

    def bootstrap_agent():
        agent_host = bootstrap_specific(("resources", "25world.xml"), clients, 1)

        agent = CLAgent.build(agent_host)

        # Jake needs to know who Sasha is, so the input signal can be attributed to the speaker correctly.
        user = Frame("@ENV.AGENT.?").add_parent("@ONT.AGENT")
        user["HAS-NAME"] = "USER"

        # Disable all of the other signal observations for optimization of this example.
        from ontocraft.observers.position import PositionSignal
        from ontocraft.observers.vision import SupervisionSignal
        agent.disable_observer(PositionSignal)
        agent.disable_observer(SupervisionSignal)

        # Make sure Jake knows how to respond to an analyzed speech act.
        agent.add_response(Frame("@ONT.SPEECH-ACT"), ChatHandleExecutable)

        while agent.host().getWorldState().is_mission_running:
            time.sleep(2)

            agent.observe(join=True)


    # Make a process for bootstrapping and running each agent; they do not need to be joined or timed otherwise.
    from multiprocessing import Process

    p1 = Process(target=bootstrap_user)
    p1.start()

    p2 = Process(target=bootstrap_agent)
    p2.start()
