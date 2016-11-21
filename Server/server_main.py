from Server.protocol import Server
import logging

FORMAT='%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()


if __name__ == '__main__':
    server = Server()
    server.listen(('127.0.0.1',7777))
    server.loop()
    LOG.info('Terminating ...')