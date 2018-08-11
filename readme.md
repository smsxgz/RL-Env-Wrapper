车辚辚，马萧萧，行人弓箭各在腰。  
耶娘妻子走相送，尘埃不见咸阳桥。  
牵衣顿足拦道哭，哭声直上干云霄。  
道旁过者问行人，行人但云点行频。  
或从十五北防河，便至四十西营田。  
去时里正与裹头，归来头白还戍边。  
边庭流血成海水，武皇开边意未已。  
君不闻，汉家山东二百州，千村万落生荆杞。  
纵有健妇把锄犁，禾生陇亩无东西。  
况复秦兵耐苦战，被驱不异犬与鸡。  
长者虽有问，役夫敢申恨？  
且如今年冬，未休关西卒。  
县官急索租，租税从何出？  
信知生男恶，反是生女好。  
生女犹得嫁比邻，生男埋没随百草。  
君不见，青海头，古来白骨无人收。  
新鬼烦冤旧鬼哭，天阴雨湿声啾啾。  
--杜甫 兵车行

-----
1. Synchronizing the environment will significantly accelerate the training of Reinforcement Learning. In this Repository, I try to implement a synchronized wrapper for both atari-like and mujoco-like environments.
1. Agent rely on gym, pyzmq, ray(multiprocessing), msgpack, numpy
1. wrappers(atari and mujoco) rely on gym, opencv, numpy.
1. Sample code is shown in script 'RL-Env-Wrapper/synchronized_wrapper/test/test.ipynb'.
1. Backend can be chosen between 'ray' and 'multiprocessing'. I pefer to 'ray'.
1. If you need a synchronized wrapper for your own environment,
    1. the environment object should have methods like 'reset', 'step', 'seed', 'close',
    1. you should offer a function which returns an environment object without arguments,
    1. if the types of 'action_space' and 'observation_space' attributes of the environment object are not 'gym.spaces.Box' or 'gym.spaces.Decrete', you should rewrite the method '\_redefine\_space' of class 'Agent' to define the new 'action_space' and 'observation_space' for synchronized wrapper.
1. TODO:
    1. Write a sample script to show how to implement OU-process.
    1. Write wrappers for dm_control.
