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
___VENDOR = 'Copyright (c) Anton Prokopov, Nikita Kirienko, Elmar Abbasov'


def __info():
    return '%s version %s (%s) %s' % (___NAME, ___VER, ___BUILT, ___VENDOR)

def client_main(args):
    c = Client()
    ui = UI(c)

    def on_recv(msg):
        if len(msg) > 0:
            if isinstance(msg, int):
                print msg
                ui.root.after(10, ui.set_cursor_pos(int(msg)))
            else:
                logging.info('\n%s' % msg)

    def on_publish():
        logging.info('\n Message published')

    def on_authorized():
        ui.getFileList()

    def on_rcv_filelist(msg):
        ui.on_filelist_received(msg)

    def on_recv_file(msg):
        t = threading.Thread(name='InputProcessor', target=ui.init(msg))
        ui.start()
        t.start()

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
