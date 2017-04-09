import sys
from ouimeaux.environment import Environment

def control(command):
    env = Environment()
    env.start()
    env.discover()
    wemo = env.list_switches()
    print(wemo)
    wemo_switch = env.get_switch(wemo[0])
    if command == 'on':
        wemo_switch.on()
    if command == 'off':
        wemo_switch.off()

if __name__ == '__main__':
    control(sys.argv[1])
