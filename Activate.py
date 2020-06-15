import argparse
import time
import sys
sys.path.insert(0, 'src')

from src.Agent import Agent

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--behaviour', type=str, required=True, help='behaviour name')
    ap.add_argument('-m', '--minutes', type=int, required=True, help='activate behaviour on X minutes')
    ap.add_argument('-d', '--delay', type=int, default=5, help='delay in seconds')
    args = vars(ap.parse_args())
    
    time.sleep(args['delay'])
    agent = Agent()
    agent.AddBehaviour(args['behaviour'], args['minutes'])
    agent.Activate()