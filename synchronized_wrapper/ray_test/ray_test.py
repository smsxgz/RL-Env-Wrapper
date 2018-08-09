import zmq
import ray
import msgpack


@ray.remote
def client(url):
    ctx = zmq.Context()
    skt = ctx.socket(zmq.REQ)
    skt.connect(url)

    for _ in range(5):
        skt.send(b'Hello!')
        print('client recv: ', skt.recv())

    skt.close()
    ctx.term()


def server(url):
    ctx = zmq.Context()
    skt = ctx.socket(zmq.REP)
    skt.bind(url)

    for _ in range(5):
        print('server recv: ', skt.recv())
        skt.send(b'World!')

    skt.close()
    ctx.term()


ray.init()
cid = client.remote('tcp://localhost:5555')
# ray.get(cid)
server('tcp://*:5555')

###################################################################
###################################################################


def server(num_server):
    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind('tcp://*:5555')

    addrs = []
    for _ in range(num_server):
        addr, empty, msg = socket.recv_multipart()
        addrs.append(addr)
        assert msg == b'ready'

    while True:
        for addr in addrs:
            socket.send_multipart([addr, b'', msgpack.dumps((2, [1, 2, 3]))])

        for _ in range(num_server):
            _, _, msg = socket.recv_multipart()
            print(msg)
            break

    socket.close()
    context.term()


@ray.remote
def client():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:5555')

    socket.send(b'ready')

    while True:
        print(msgpack.loads(socket.recv()))
        socket.send(b'hello!')
        break

    socket.close()
    context.term()


[client.remote() for i in range(4)]

server(4)
