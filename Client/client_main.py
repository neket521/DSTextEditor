from Client.client_protocol import Client
from GUI.GUI import UI
from time import asctime, localtime
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
            msg = msg.split(' ')
            msg = tuple(msg[:3] + [' '.join(msg[3:])])
            #t_form = lambda x: asctime(localtime(float(x)))
            #m_form = lambda x: '%s [%s:%s] -> ' \
            #                   '%s' % (t_form(x[0]), x[1], x[2], x[3].decode('utf-8'))
            #m = m_form(msg)
            print(msg)
            #logging.info('\n%s' % msg)

    def on_publish():
        logging.info('\n Message published')

    def on_authorized():
        ui.init()
        #c.loop()


    c.set_on_published_callback(on_publish)
    c.set_on_recv_callback(on_recv)
    c.set_on_authorized_callback(on_authorized)

    if c.connect((args.host, int(args.port))):
        u, p = ui.getpwd().split(',')
        c.handshake(u, p)
        c.loop()

    logging.info('Terminating')
