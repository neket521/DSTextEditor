from Client.client_protocol import Client
from threading import Thread
from time import asctime, localtime
import logging, time

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


def handle_user_input(myclient):
    logging.info('Starting input processor')

    while 1:
        logging.info('\nHit Enter to init user-input ...')
        raw_input('')
        logging.info('\nEnter message to send to all or Q to exit: ')
        m = raw_input('')
        if len(m) <= 0:
            continue
        elif m == 'Q':
            myclient.stop()
            return
        else:
            myclient.send_short_message(m)


def client_main(args):
    def on_recv(msg):
        if len(msg) > 0:
            msg = msg.split(' ')
            msg = tuple(msg[:3] + [' '.join(msg[3:])])
            t_form = lambda x: asctime(localtime(float(x)))
            m_form = lambda x: '%s [%s:%s] -> ' \
                               '%s' % (t_form(x[0]), x[1], x[2], x[3].decode('utf-8'))
            m = m_form(msg)
            logging.info('\n%s' % m)

    def on_publish():
        logging.info('\n Message published')

    def on_authorized():
        t = Thread(name='InputProcessor', target=handle_user_input, args=(c,))
        t.start()

    c = Client()
    c.set_on_published_callback(on_publish)
    c.set_on_recv_callback(on_recv)
    c.set_on_authorized_callback(on_authorized)

    if c.connect((args.host, int(args.port))):
        # start UI, ask for username and password
        # send handshake
        c.handshake('elmar', '000')
        time.sleep(5)
        # t.join()
        logging.info('Couldn\'t authenticate, terminating')
