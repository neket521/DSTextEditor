import logging
FORMAT='%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()
from threading import Thread, Lock
from socket import AF_INET, SOCK_STREAM, socket



class ClientSession(Thread):

    def __init__(self,soc,soc_addr):
        Thread.__init__(self)
        self.__s = soc
        self.__addr = soc_addr
        self.__m_last = 0
        self.__send_lock = Lock()
        LOG.info('Client %s:%d connected' % self.__addr)

    ########################
    # Place to add methods



class Server():

    def __init__(self):
        LOG.info('Initiating ...')

    def listen(self,sock_addr,backlog=1):
        self.__sock_addr = sock_addr
        self.__backlog = backlog
        self.__s = socket(AF_INET, SOCK_STREAM)
        self.__s.bind(self.__sock_addr)
        self.__s.listen(self.__backlog)
        LOG.debug( 'Socket %s:%d is in listening state'\
                       '' % self.__s.getsockname() )

    def loop(self):
        LOG.info( 'Falling to serving loop, press Ctrl+C to terminate ...' )
        clients = []


        try:
            while 1:
                client_socket = None
                LOG.info( 'Awaiting new clients ...' )
                client_socket,client_addr = self.__s.accept()
                c = ClientSession(client_socket,client_addr)
                clients.append(c)
                c.start()
        except KeyboardInterrupt:
            LOG.warn( 'Ctrl+C issued closing server ...' )
        finally:
            if client_socket != None:
                client_socket.close()
            self.__s.close()
        map(lambda x: x.join(),clients)

