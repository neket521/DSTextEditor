from Server.server_protocol import Server
import logging

FORMAT = '%(asctime)s (%(threadName)-2s) %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

# Constants -------------------------------------------------------------------
___NAME = 'DSTextEditor Server'
___VER = '0.1'
___DESC = 'Collaborative Text Editor Server'
___BUILT = '2016-11-24'
___VENDOR = 'Copyright (c) Anton Prokopov, Nikita Kirienko, Elmar Abbasov'


def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)

def server_main(args):
    server = Server()
    server.listen((args.listenaddr, int(args.listenport)))
    server.loop()
    LOG.info('Terminating ...')
