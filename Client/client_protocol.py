import logging, hashlib
from threading import Lock
from socket import AF_INET, SOCK_STREAM, socket, SHUT_RD
from socket import error as soc_err
from common import DEFAULT_BUFSIZE, RSP_UNKNCONTROL, REQ_SEND, RSP_OK_AUTH, RSP_ERR_AUTH, \
    MSG_SEP, MSG_FIELD_SEP, RSP_OK_SEND, RSP_OK_GET, RSP_NOTIFY, REQ_GET, REQ_AUTH, \
    RSP_OK_GETF, REQ_GETF, REQ_SP, RSP_OK_SP, REQ_SENDF, REQ_SFN,RSP_OK_SFN

FORMAT = '%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

class Client():

    def __init__(self):
        self.__send_lock = Lock()
        self.__on_recv = None
        self.__on_recv_filelist = None
        self.__on_published = None
        self.__on_authorized = None
        self.__on_recv_file = None
        self.__token = None

    def set_on_recv_file_callback(self, on_recv_file_f):
        self.__on_recv_file = on_recv_file_f

    def set_on_recv_callback(self, on_recv_f):
        self.__on_recv = on_recv_f

    def set_on_recv_filelist_callback(self, on_recv_filelist_f):
        self.__on_recv_filelist = on_recv_filelist_f

    def set_on_published_callback(self, on_published_f):
        self.__on_published = on_published_f

    def set_on_authorized_callback(self, on_authorized_f):
        self.__on_authorized = on_authorized_f

    def stop(self):
        self.__s.shutdown(SHUT_RD)
        self.__s.close()

    def connect(self, srv_addr):
        self.__s = socket(AF_INET, SOCK_STREAM)
        try:
            self.__s.connect(srv_addr)
            logging.info('Connected to server at %s:%d' % srv_addr)
            return True
        except soc_err as e:
            logging.error('Can not connect server at %s:%d' \
                          ' %s ' % (srv_addr + (str(e),)))
        return False

    def __session_rcv(self):
        m, b = '', ''
        try:
            b = self.__s.recv(DEFAULT_BUFSIZE)
            m += b
            while len(b) > 0 and not (b.endswith(MSG_SEP)):
                b = self.__s.recv(DEFAULT_BUFSIZE)
                m += b
            if len(b) <= 0:
                logging.debug('Socket receive interrupted')
                self.__s.close()
                m = ''
            m = m[:-1]
        except KeyboardInterrupt:
            self.__s.close()
            logging.info('Ctrl+C issued, terminating ...')
            m = ''
        except soc_err as e:
            if e.errno == 107:
                logging.warn('Server closed connection, terminating ...')
            else:
                logging.error('Connection error: %s' % str(e))
            self.__s.close()
            logging.info('Disconnected')
            m = ''
        return m

    def __session_send(self, msg):
        if self.__token is not None:
            m = msg + MSG_FIELD_SEP + self.__token + MSG_SEP
        else:
            m = msg + MSG_SEP
        with self.__send_lock:
            r = False
            try:
                self.__s.sendall(m)
                r = True
            except KeyboardInterrupt:
                self.__s.close()
                logging.info('Ctrl+C issued, terminating ...')
            except soc_err as e:
                if e.errno == 107:
                    logging.warn('Server closed connection, terminating ...')
                else:
                    logging.error('Connection error: %s' % str(e))
                self.__s.close()
                logging.info('Disconnected')
            return r

    def __protocol_rcv(self, message):
        logging.debug('Received [%d bytes] in total' % len(message))
        if len(message) < 2:
            logging.debug('Not enough data received from %s ' % message)
            return
        logging.debug('Response control code (%s)' % message[0])
        if message.startswith(RSP_OK_SEND + MSG_FIELD_SEP):
            logging.debug('Server confirmed message was published')
            self.__on_published()
        elif message.startswith(RSP_ERR_AUTH):
            logging.debug('Not authorized')
        elif message.startswith(RSP_OK_AUTH + MSG_FIELD_SEP):
            token = message.split(MSG_FIELD_SEP)[1]
            self.__token = token
            self.__on_authorized()
        elif message.startswith(RSP_NOTIFY + MSG_FIELD_SEP):
            logging.debug('Server notification received, fetching messages')
            # self.__fetch_msgs()
        elif message.startswith(RSP_OK_GET + MSG_FIELD_SEP):
            logging.debug('Messages retrieved ...')
            msgs = message[2:].split(MSG_FIELD_SEP)
            for m in msgs:
                self.__on_recv(m)
        elif message.startswith(RSP_OK_GETF + MSG_FIELD_SEP):
            logging.debug('Filelist received ...')
            m = message[3:] #RSP_OK_GETF has already 2 symbols + 1 for separator ':' = offset of 3
            self.__on_recv_filelist(m)
        elif message.startswith(RSP_OK_SFN + MSG_FIELD_SEP):
            logging.debug('File received ...')
            m = message[3:]
            self.get_file(m)
        elif message.startswith(RSP_OK_SP + MSG_FIELD_SEP):
            logging.debug('Line available ...')
            #print("line")
            #m = message[3:]
            #self.__on_recv(m)
            #need to call update method from gui if
        else:
            logging.debug('Unknown control message received: %s ' % message)
            return RSP_UNKNCONTROL

    def loop(self):
        logging.info('Falling to receiver loop ...')
        #self.__fetch_msgs()
        while 1:
            m = self.__session_rcv()
            if len(m) <= 0:
                break
            self.__protocol_rcv(m)

    def handshake(self, username, password):
        hash_obj = hashlib.md5()
        hash_obj.update(password)
        req = REQ_AUTH + MSG_FIELD_SEP + username + MSG_FIELD_SEP + hash_obj.hexdigest()
        return self.__session_send(req)

    # should be modified to fetch the whole file and the changes from the queue
    def __fetch_document(self):
        req = REQ_GET + MSG_FIELD_SEP
        return self.__session_send(req)

    # send updated line
    def send_short_message(self, message):
        logging.info("sending short message")
        req = REQ_SEND + MSG_FIELD_SEP + message
        return self.__session_send(req)

    def send_position(self, message):
        logging.info("sending current line number")
        req = REQ_SP + MSG_FIELD_SEP + message
        return self.__session_send(req)

    def get_filelist(self):
        logging.info("sending request for retrieving available files")
        req = REQ_GETF + MSG_FIELD_SEP + 'getFiles'
        return self.__session_send(req)

    def send_filename(self,message):
        logging.info("sending filename")
        req = REQ_SFN + MSG_FIELD_SEP + message
        return self.__session_send(req)

    # send the whole file
    def send_long_message(self, message):
        # split message into chunks of size DEFAULT_BUFSIZE and send all the chunks to server
        logging.info("sending long message")
        l = [message[i:i + DEFAULT_BUFSIZE] for i in range(0, len(message), DEFAULT_BUFSIZE)]
        req = REQ_SENDF + MSG_FIELD_SEP
        self.__session_send(req)
        for chunk in l:
            req = REQ_SEND + MSG_FIELD_SEP + "".join(chunk)
            self.__session_send(req)
        req = REQ_SENDF + MSG_FIELD_SEP
        self.__session_send(req)
        logging.info("long message sending complete")

    def get_file(self,message):
        self.__on_recv_file(message)



