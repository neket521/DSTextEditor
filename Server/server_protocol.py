from threading import Thread, Lock
from socket import AF_INET, SOCK_STREAM, socket
from socket import error as soc_err
from time import time
from queue import Queue
from common import DEFAULT_BUFSIZE, RSP_UNKNCONTROL, REQ_SEND, RSP_OK_AUTH, RSP_ERR_AUTH, \
    MSG_SEP, MSG_FIELD_SEP, RSP_OK_SEND, RSP_OK_GET, RSP_NOTIFY, RSP_BADFORMAT, REQ_GET, REQ_AUTH, REQ_GETLF, RSP_OK_GETLF, \
    REQ_GETF, RSP_OK_SP, REQ_SP, RSP_OK_GETF,REQ_SHR
import logging, uuid, os

FORMAT = '%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class ClientSession(Thread):

    def __init__(self, soc, soc_addr, server):
        Thread.__init__(self)
        self.__s = soc
        self.__addr = soc_addr
        self.linenr = 0
        self.__send_lock = Lock()
        self.__serv = server
        self.__login = ''
        self.__token = ''
        self.__last_linenr = None
        self.__filename = '' # when filename is updated, queue has to be reinitialized,
                             # but before previously initialized queue should write all the changes to the file

    def __save_message(self, msg):
        self.__serv.save_message(self.__filename, self.linenr, msg, self.__addr)

    def __get(self):
        msgs = self.__serv.get_messages()
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
                LOG.warn('Client %s:%d left before server could handle it' % self.__addr)
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
        if len(chunks) >= 3 and chunks[len(chunks)-1].strip(';') == self.__token:
            if message.startswith(REQ_SEND + MSG_FIELD_SEP):
                msg = message.split(MSG_FIELD_SEP)[1]
                LOG.debug('Client %s:%d will publish: ' \
                          '%s' % (self.__addr + ((msg[:60] + '...' if len(msg) > 60 else msg),)))
                self.__save_message(msg)
                LOG.info('Published new message')
                return RSP_OK_SEND + MSG_FIELD_SEP
            elif message.startswith(REQ_GET + MSG_FIELD_SEP):
                msgs = self.__get()
                msgs = map(lambda x: ' '.join(map(str, x)), msgs)
                msgs = MSG_FIELD_SEP.join(tuple(msgs))
                return RSP_OK_GET + MSG_FIELD_SEP + msgs
            elif message.startswith(REQ_SP + MSG_FIELD_SEP):
                linenr = int(message.split(MSG_FIELD_SEP)[1])
                if self.__last_linenr != linenr:
                    self.__serv.unlock_line(self.__last_linenr, self.__login)
                    self.__serv.lock_line(linenr, self.__login)
                else:
                    while not self.__serv.lock_line(linenr, self.__login):
                        linenr += 1
                self.__last_linenr = linenr
                LOG.info("Line " + str(linenr))
                return RSP_OK_SP + MSG_FIELD_SEP + str(linenr)
            elif message.startswith(REQ_GETLF + MSG_FIELD_SEP):
                msg = ''
                with open('Server/Database/' + "filelist.txt", 'r') as f:
                    for line in f:
                        line_parts = line.split(';')
                        if line_parts[2].__contains__(self.__login) or line_parts[1] == self.__login:
                            msg += line_parts[0] + ',' # this could be huge
                f.close()
                LOG.info('Filelist sent')
                return RSP_OK_GETLF + MSG_FIELD_SEP + msg
            elif message.startswith(REQ_SHR + MSG_FIELD_SEP):
                filename, shared_with = message.split(MSG_FIELD_SEP)[1:3]
                lines = []
                with open('Server/Database/' + "filelist.txt", 'r') as f:
                    for line in f:
                        lines.append(line)
                with open('Server/Database/' + "filelist.txt", 'w') as f:
                    for i in range(len(lines)):
                        if lines[i].split(';')[0] == filename:
                            if not lines[i].split(';')[2].__contains__(shared_with):
                                lines[i] = filename + ';' + lines[i].split(';')[1] + ';' + shared_with + '\n'
                                print lines[i]
                    f.writelines(lines)
                LOG.info('File '+filename+' is shared with '+shared_with)
                return "90:" # what the hell is this?
            elif message.startswith(REQ_GETF + MSG_FIELD_SEP):
                self.filename = message.split(MSG_FIELD_SEP)[1]
                if not self.filename.__contains__('.txt'):
                    self.filename += '.txt'
                if os.path.isfile('Server/UserFiles/' + self.filename):
                    with open('Server/UserFiles/' + self.filename, 'r') as f:
                        LOG.info('file opened')
                        LOG.info('receiving data...')
                        LOG.info('receiving data...')
                        for line in f.readlines():
                            self.__s.send(RSP_OK_GETF + MSG_FIELD_SEP + line)
                    LOG.info('Successfully read the file and sent its contents back to client')
                    f.close()
                    return RSP_OK_GETF + MSG_FIELD_SEP
                else:
                    nf = open('Server/UserFiles/' + self.filename, 'w')
                    nf.close()
                    with open('Server/Database/' + "filelist.txt", 'a') as f:
                        f.write('\n')
                        f.write(self.filename + ';' + self.__login + ';')
                    f.close()
                    return RSP_OK_GETF + MSG_FIELD_SEP
            else:
                LOG.debug('Unknown control message received: %s ' % message)
                return RSP_UNKNCONTROL
        elif message.startswith(REQ_AUTH + MSG_FIELD_SEP):
            code, u, p = message.split(MSG_FIELD_SEP)
            if p == self.get_passwd_hash_by_username(u):
                self.__login = u
                self.__token = uuid.uuid4().hex
                LOG.info('Auth success, token sent back')
                return RSP_OK_AUTH + MSG_FIELD_SEP + self.__token
            else:
                LOG.info('Auth failed')
                return RSP_ERR_AUTH + MSG_FIELD_SEP

        else:
            # authentication failed
            LOG.info('Auth failed')
            return RSP_ERR_AUTH + MSG_FIELD_SEP

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
        result = None
        for line in f:
            if line.startswith(username):
                result = line.split(':')[1].strip('\n')
        f.close()
        return result

class Server:

    def __init__(self):
        self.__msgs = Queue()
        self.__on_save = None
        self.__lock = Lock()
        self.__locked_lines = []

    def listen(self, sock_addr, backlog=1):
        self.__sock_addr = sock_addr
        self.__backlog = backlog
        self.__s = socket(AF_INET, SOCK_STREAM)
        self.__s.bind(self.__sock_addr)
        self.__s.listen(self.__backlog)
        LOG.debug('Socket %s:%d is in listening state' % self.__s.getsockname())

    def loop(self):
        LOG.info('Falling to serving loop, press Ctrl+C to terminate ...')
        clients = []

        def __on_save_message():
            for c in clients:
                c.notify()

        self.set_on_save_callback(__on_save_message)

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

    def save_message(self, filename, line, msg, source):
        with self.__lock:
            ip, port = source
            t = time()
            self.__msgs.add((t, ip, port, filename, line, msg))
        self.__on_save()

    def get_messages(self):
        msgs = []
        with self.__lock:
            self.__msgs.get_messages()
        return msgs

    def lock_line(self, linenr, user):
        for el in self.__locked_lines:
            if el[0] == linenr and el[1] != user:
                return False
            elif el[0] == linenr and el[1] == user:
                return True
        self.__locked_lines.append((linenr, user))
        print self.__locked_lines
        return True

    def unlock_line(self, linenr, user):
        for el in self.__locked_lines:
            if el[0] == linenr and el[1] == user:
                self.__locked_lines.remove((linenr, user))
        print self.__locked_lines
