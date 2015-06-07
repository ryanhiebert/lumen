from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from contextlib import closing


class ProjectorSet(object):
    def __init__(self, ip_addrs):
        self.projectors = [Projector(ip_addr) for ip_addr in ip_addrs]

    def __repr__(self):
        return 'ProjectorSet({})'.format(
            repr([p.ip_addr for p in self.projectors]))

    def query(self, message):
        return [projector.query(message) for projector in self.projectors]

    def poweron(self):
        return [projector.poweron() for projector in self.projectors]

    def poweroff(self):
        return [projector.poweroff() for projector in self.projectors]

    def freeze(self):
        return [projector.freeze() for projector in self.projectors]

    def unfreeze(self):
        return [projector.unfreeze() for projector in self.projectors]

    def blank(self):
        return [projector.blank() for projector in self.projectors]

    def unblank(self):
        return [projector.unblank() for projector in self.projectors]


class Projector(object):
    def __init__(self, ip_addr):
        self.port = 33336
        self.ip_addr = ip_addr

    def __repr__(self):
        return 'Projector({})'.format(repr(self.ip_addr))

    def query(self, message):
        with closing(socket(AF_INET, SOCK_STREAM)) as s:
            s.connect((self.ip_addr, self.port))
            bytes = s.send(message + b'\r')
            messageback = s.recv(128)
            s.shutdown(SHUT_RDWR)
        assert messageback.endswith(b'\r')
        return Response(messageback[:-1])

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

