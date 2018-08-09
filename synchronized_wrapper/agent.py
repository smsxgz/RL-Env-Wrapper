import os
import ray
import zmq
import msgpack
import numpy as np
import msgpack_numpy
from collections import OrderedDict

from subagent import subagent

msgpack_numpy.patch()


class Agent:
    def __init__(self, num_agents, make_env_fn, basename):
        ray.init()

        self._num_agents = num_agents

        env = make_env_fn()
        self.observation_space = env.observation_space
        self.action_space = env.action_space
        env.close()

        url_path = './.ipc/{}-Agent.ipc'.format(basename)
        if os.path.exists(url_path):
            os.remove(url_path)
        url = 'ipc://{}'.format(url_path)
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.ROUTER)
        self._socket.bind(url)

        # Run subagents
        [subagent.remote(make_env_fn, i, url) for i in range(num_agents)]

        self.addrs = OrderedDict()

        # Waiting for message b'ready' from each subagent
        for _ in range(self.num_agents):
            addr, empty, msg = self.agent_socket.recv_multipart()
            self.addrs[addr] = None
            assert msg == b'ready'
        print('All subagents are ready! ')

    def reset(self):
        for addr in self.addrs:
            self.agent_socket.send_multipart([addr, b'', b'reset'])
        for _ in range(self.num_agents):
            addr, empty, msg = self.agent_socket.recv_multipart()
            msg = msgpack.loads(msg)
            self.addrs[addr] = msg
        return np.array(list(self.addrs.values()))

    def step(self, actions):
        for action, addr in zip(actions, self.addrs.keys()):
            self.agent_socket.send_multipart(
                [addr, b'', msgpack.dumps(action)])

        info = {}
        for _ in range(self.num_agents):
            addr, empty, msg = self.agent_socket.recv_multipart()
            msg = msgpack.loads(msg)
            if msg[-1]:
                info[addr] = msg[-1]
            self.addrs[addr] = msg[:-1]
        states, rewards, dones = map(np.array, zip(*self.addrs.values()))
        return states, rewards, dones, info

    def close(self):
        for addr in self.addrs:
            self.agent_socket.send_multipart([addr, b'', b'close'])
        self.agent_socket.close()
        self.context.term()
