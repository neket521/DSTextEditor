'''
Created on Oct 18, 2016

@author: devel
'''
import logging
FORMAT='%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)
from threading import Thread, Lock
from socket import AF_INET, SOCK_STREAM, socket, SHUT_RD
from socket import error as soc_err
import time
class Client():

    def __init__(self):
        self.__send_lock = Lock()
        self.__on_recv = None
        self.__on_published = None

    def stop(self):
        self.__s.shutdown(SHUT_RD)
        self.__s.close()

    def loop(self):
        while(True):
            time.sleep(5)

    def connect(self,srv_addr):
        self.__s = socket(AF_INET,SOCK_STREAM)
        try:
            self.__s.connect(srv_addr)
            logging.info('Connected to server at %s:%d' % srv_addr)
            return True
        except soc_err as e:
            logging.error('Can not connect server at %s:%d'\
                      ' %s ' % (srv_addr+(str(e),)))
        return False





