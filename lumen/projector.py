from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from contextlib import closing, contextmanager, ExitStack


class Projector(object):
    def __init__(self, ip_addr):
        self.port = 33336
        self.ip_addr = ip_addr

    def __repr__(self):
        return 'Projector({})'.format(repr(self.ip_addr))

    @contextmanager
    def connect(self):
        with Socket.connect(self.ip_addr, self.port) as s:
            yield s

    def query(self, message):
        with self.connect() as s:
            s.send(message)
            return s.recv()

    def poweron(self):
        return self.query(b'POWER=ON')

    def poweroff(self):
        return self.query(b'POWER=OFF')

    def freeze(self):
        return self.query(b'FREEZE=ON')

    def unfreeze(self):
        return self.query(b'FREEZE=OFF')

    def blank(self):
        return self.query(b'BLANK=ON')

    def unblank(self):
        return self.query(b'BLANK=OFF')


class ProjectorSet(Projector):
    """A Projector subclass that control multiple projectors."""

    def __init__(self, ip_addrs):
        self.projectors = [Projector(ip_addr) for ip_addr in ip_addrs]

    def __repr__(self):
        return 'ProjectorSet({})'.format(
            repr([p.ip_addr for p in self.projectors]))

    @contextmanager
    def connect(self):
        with ExitStack() as stack:
            yield [
                stack.enter_context(projector.connect())
                for projector in self.projectors
            ]

    def query(self, message):
        with self.connect() as sockets:
            [s.send(message) for s in sockets]
            return [s.recv() for s in sockets]


class Socket:
    """Wrap a socket to make messaging easier.

    This isn't a subclass of socket because socket doesn't
    play well with subclasses.
    """
    def __init__(self, socket, ip_addr, port):
        self.socket = socket
        socket.connect((ip_addr, port))

    def send(self, bytes, *args, **kwargs):
        return self.socket.send(bytes + b'\r', *args, **kwargs)

    def recv(self, bufsize=128, *args, **kwargs):
        res = self.socket.recv(bufsize, *args, **kwargs)
        assert res.endswith(b'\r')
        return Response(res[:-1])

    def close(self, *args, **kwargs):
        # Shut down the socket when closing it
        self.socket.shutdown(SHUT_RDWR)
        return self.socket.close(*args, **kwargs)

    @classmethod
    @contextmanager
    def connect(cls, ip_addr, port):
        sock = socket(AF_INET, SOCK_STREAM)
        with closing(Socket(sock, ip_addr, port)) as s:
            yield s


class Response(object):
    Normal = b'i'
    Reference = b'g'
    Error = b'e'

    def __init__(self, response):
        self.type, self.message = response.split(b':', 1)

    def __repr__(self):
        return 'Response({})'.format(
            repr(b':'.join([self.type, self.message])))

    def normal(self):
        """Parse a normal response."""
        if self.type != self.Normal:
            raise RuntimeError('Incorrect type.')
        return message

    def reference(self):
        """Parse a reference command response."""
        if self.type != self.Reference:
            raise RuntimeError('Incorrect type.')
        command, value = self.message.split(b'=', 1)
        return command, value

    def error(self):
        """Parse an error response."""
        if self.type != self.Error:
            raise RuntimeError('Incorrect type.')
        code, info = self.message.split(b' ')
        return code, info

