from threading import Thread, Lock
from socket import AF_INET, SOCK_STREAM, socket
from socket import error as soc_err
from time import time
from common import DEFAULT_BUFSIZE, RSP_UNKNCONTROL, REQ_SEND, RSP_OK_AUTH, RSP_ERR_AUTH, \
    MSG_SEP, MSG_FIELD_SEP, RSP_OK_SEND, RSP_OK_GET, RSP_NOTIFY, RSP_BADFORMAT, REQ_GET, REQ_AUTH
import logging, uuid, os

FORMAT = '%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class ClientSession(Thread):
    def __init__(self, soc, soc_addr, server):
        Thread.__init__(self)
        self.__s = soc
        self.__addr = soc_addr
        self.__m_last = 0
        self.__send_lock = Lock()
        self.__serv = server
        self.__login = ""
        self.__token = ""

    def __save_message(self, msg):
        self.__m_last = self.__serv.save_message(msg, self.__addr)

    def __get(self):
        msgs = self.__serv.get_messages(self.__m_last)
        self.__m_last = 1  # if new message received, then immediately update clients with this 1 message, no need to display n last messages
        return msgs

    def __session_rcv(self):
        m, b = '', ''
        try:
            b = self.__s.recv(DEFAULT_BUFSIZE)
            m += b
            while len(b) > 0 and not (b.endswith(MSG_SEP)):
                b = self.__s.recv(DEFAULT_BUFSIZE)
                m += b
            if len(b) <= 0:
                self.__s.close()
                LOG.info('Client %s:%d disconnected' % self.__addr)
                m = ''
            m = m[:-1]
        except KeyboardInterrupt:
            self.__s.close()
            LOG.info('Ctrl+C issued, disconnecting client %s:%d' % self.__addr)
            m = ''
        except soc_err as e:
            if e.errno == 107:
                LOG.warn('Client %s:%d left before server could handle it' \
                         '' % self.__addr)
            else:
                LOG.error('Error: %s' % str(e))
            self.__s.close()
            LOG.info('Client %s:%d disconnected' % self.__addr)
            m = ''
        return m

    def __protocol_rcv(self, message):
        LOG.debug('Received request [%d bytes] in total' % len(message))
        if len(message) < 2:
            LOG.degug('Not enough data received from %s ' % message)
            return RSP_BADFORMAT
        LOG.debug('Request control code (%s)' % message[0])
        chunks = message.split(MSG_FIELD_SEP)
        if len(message.split(MSG_FIELD_SEP)) >= 3 and chunks[2].strip(';') == self.__token:
            if message.startswith(REQ_SEND + MSG_FIELD_SEP):
                msg = message.split(MSG_FIELD_SEP)[1]
                # msg = deserialize(msg)
                LOG.debug('Client %s:%d will publish: ' \
                          '%s' % (self.__addr + ((msg[:60] + '...' if len(msg) > 60 else msg),)))
                self.__save_message(msg)
                LOG.info('Published new message')
                return RSP_OK_SEND + MSG_FIELD_SEP
            elif message.startswith(REQ_GET + MSG_FIELD_SEP):
                msgs = self.__get()
                msgs = map(lambda x: ' '.join(map(str, x)), msgs)
                # msgs = map(serialize,msgs)
                msgs = MSG_FIELD_SEP.join(tuple(msgs))
                return RSP_OK_GET + MSG_FIELD_SEP + msgs
            else:
                LOG.debug('Unknown control message received: %s ' % message)
                return RSP_UNKNCONTROL
        elif message.startswith(REQ_AUTH + MSG_FIELD_SEP):
            code, u, p = message.split(MSG_FIELD_SEP)
            if p == self.get_passwd_hash_by_username(u):
                self.__login = u
                self.__token = uuid.uuid4().hex
                return RSP_OK_AUTH + MSG_FIELD_SEP + self.__token
            else:
                return RSP_ERR_AUTH
        else:
            # authentication failed
            LOG.info('Auth failed')
            return RSP_ERR_AUTH

    def __session_send(self, msg):
        m = msg + MSG_SEP
        with self.__send_lock:
            r = False
            try:
                self.__s.sendall(m)
                r = True
            except KeyboardInterrupt:
                self.__s.close()
                LOG.info('Ctrl+C issued, disconnecting client %s:%d' \
                         '' % self.__addr)
            except soc_err as e:
                if e.errno == 107:
                    LOG.warn('Client %s:%d left before server could handle it' \
                             '' % self.__addr)
                else:
                    LOG.error('Error: %s' % str(e))
                self.__s.close()
                LOG.info('Client %s:%d disconnected' % self.__addr)
            return r

    def notify(self):
        self.__session_send(RSP_NOTIFY + MSG_FIELD_SEP)

    def run(self):
        while 1:
            m = self.__session_rcv()
            if len(m) <= 0:
                break
            rsp = self.__protocol_rcv(m)
            if not self.__session_send(rsp):
                break

    def get_passwd_hash_by_username(self, username):
        dir = os.path.dirname(__file__)
        rel_path = 'Database/users.txt'
        path = os.path.join(dir, rel_path)
        f = open(path, 'r')
        for line in f:
            if line.startswith(username):
                return line.split(':')[1].strip('\n')
        return None


class Server():
    def __init__(self):
        self.__msgs = []
        self.__lock = Lock()
        self.__on_save = None

    def listen(self, sock_addr, backlog=1):
        self.__sock_addr = sock_addr
        self.__backlog = backlog
        self.__s = socket(AF_INET, SOCK_STREAM)
        self.__s.bind(self.__sock_addr)
        self.__s.listen(self.__backlog)
        LOG.debug('Socket %s:%d is in listening state' \
                  '' % self.__s.getsockname())

    def loop(self):
        LOG.info('Falling to serving loop, press Ctrl+C to terminate ...')
        clients = []

        def __on_publish():
            for c in clients:
                c.notify()

        self.set_on_save_callback(__on_publish)

        try:
            while 1:
                client_socket = None
                LOG.info('Awaiting new clients ...')
                client_socket, client_addr = self.__s.accept()
                c = ClientSession(client_socket, client_addr, self)
                clients.append(c)
                c.start()
        except KeyboardInterrupt:
            LOG.warn('Ctrl+C issued closing server ...')
        finally:
            if client_socket != None:
                client_socket.close()
            self.__s.close()
        map(lambda x: x.join(), clients)

    def set_on_save_callback(self, on_save_f):
        self.__on_save = on_save_f

    def save_message(self, msg, source):
        with self.__lock:
            ip, port = source
            t = time()
            self.__msgs.append((t, ip, port, msg))
        self.__on_save()

    def get_messages(self, start):
        msgs = []
        with self.__lock:
            if len(self.__msgs) > 0:
                msgs = [m for m in self.__msgs[start:]]
        return msgs