from agent import Agent
from environment import Environment
from pprint import PrettyPrinter
import time

if __name__ == '__main__':
    env = Environment(10, 10)
    env.add_agent(5,5)

    pp = PrettyPrinter()
    pp.pprint(env.cells)

    while(True):
        env.tick()
        pp.pprint(env.cells)
        time.sleep(5)