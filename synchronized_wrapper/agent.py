import os
import ray
import zmq
import msgpack
import numpy as np
import msgpack_numpy
from gym.spaces.box import Box
from collections import OrderedDict

from .subagent import subagent

ray.init()
msgpack_numpy.patch()


class Agent:
    def __init__(self, num_agents, env_fn, basename):
        self._num_agents = num_agents

        env = env_fn()
        ob_space = env.observation_space
        self.observation_space = Box(
            low=np.repeat([ob_space.low], num_agents, axis=0),
            high=np.repeat([ob_space.high], num_agents, axis=0),
            dtype=np.float32)
        self.action_space = env.action_space
        env.close()

        base_path = './.ipc'
        if not os.path.exists(base_path):
            os.mkdir(base_path)

        url_path = os.path.join(base_path, '{}-Agent.ipc'.format(basename))
        if os.path.exists(url_path):
            os.remove(url_path)

        url = 'ipc://{}'.format(url_path)
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.ROUTER)
        self._socket.bind(url)

        # Run subagents
        [subagent.remote(env_fn, i, url) for i in range(num_agents)]

        self.addrs = OrderedDict()

        # Waiting for message b'ready' from each subagent
        for _ in range(self._num_agents):
            addr, empty, msg = self._socket.recv_multipart()
            self.addrs[addr] = None
            assert msg == b'ready'
        print('All subagents are ready! ')

    def reset(self):
        for addr in self.addrs:
            self._socket.send_multipart([addr, b'', b'reset'])
        for _ in range(self._num_agents):
            addr, empty, msg = self._socket.recv_multipart()
            msg = msgpack.loads(msg)
            self.addrs[addr] = msg
        return np.array(list(self.addrs.values()))

    def step(self, actions):
        for action, addr in zip(actions, self.addrs.keys()):
            self._socket.send_multipart([addr, b'', msgpack.dumps(action)])

        info = {}
        for _ in range(self._num_agents):
            addr, empty, msg = self._socket.recv_multipart()
            msg = msgpack.loads(msg)
            if msg[-1]:
                info[addr] = msg[-1]
            self.addrs[addr] = msg[:-1]
        states, rewards, dones = map(np.array, zip(*self.addrs.values()))
        return states, rewards, dones, info

    def close(self):
        for addr in self.addrs:
            self._socket.send_multipart([addr, b'', b'close'])
        self._socket.close()
        self._context.term()
