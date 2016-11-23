from Client.client_protocol import Client
from GUI.GUI import UI
from threading import Thread
import logging

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

# Constants -------------------------------------------------------------------
___NAME = 'DSTextEditor Client'
___VER = '0.1'
___DESC = 'Collaborative Text Editor Client'
___BUILT = '2016-11-24'
___VENDOR = 'Copyright (c) Anton Prokopov, Nikita Kirienko, Elmar Abbasov'


def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)

def client_main(args):
    c = Client()
    ui = UI(c)

    def on_recv(msg):
        if len(msg) > 0:
            logging.info('\n%s' % msg)

    def on_publish():
        logging.info('\n Message published')

    def on_authorized():
        t = Thread(name='InputProcessor', target=ui.init)
        t.start()

    c.set_on_published_callback(on_publish)
    c.set_on_recv_callback(on_recv)
    c.set_on_authorized_callback(on_authorized)

    if c.connect((args.host, int(args.port))):
        u, p = ui.getpwd().split(',')
        c.handshake(u, p)
        c.loop()

    logging.info('Terminating')
