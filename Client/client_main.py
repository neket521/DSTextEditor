from Client.client_protocol import Client
from GUI.GUI import UI
import logging
import threading

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

# Constants -------------------------------------------------------------------
___NAME = 'DSTextEditor Client'
___VER = '0.1'
___DESC = 'Collaborative Text Editor Client'
___BUILT = '2016-11-24'
VENDOR = 'Copyright (c) Anton Prokopov, Nikita Kirienko, Elmar Abbasov'


def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, VENDOR)

def client_main(args):
    c = Client()
    ui = UI(c)

    def on_recv(msg):
        if len(msg) > 0:
            logging.info('\n%s' % msg)

    def on_publish():
        logging.info('\n Message published')

    def on_authorized():
        ui.getFileList()
        #t = threading.Thread(name='InputProcessor', target=ui.getFileList())
        #t.start()

    def on_rcv_filelist(msg):
        ui.on_filelist_received(msg)

    def on_recv_file(msg):
        ui.init()
        # Вот этот метод  ui.put_message(msg) должен срабатывать во время работы УИ а он срабатывает только после закрытия
        ui.put_message(msg)


    c.set_on_published_callback(on_publish)
    c.set_on_recv_callback(on_recv)
    c.set_on_authorized_callback(on_authorized)
    c.set_on_recv_filelist_callback(on_rcv_filelist)
    c.set_on_recv_file_callback(on_recv_file)

    if c.connect((args.host, int(args.port))):
        u, p = ui.getpwd().split(',')
        c.handshake(u, p)
        c.loop()

    logging.info('Terminating')
