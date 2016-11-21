from Client.client_protocol import Client
import logging

FORMAT='%(asctime)s %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)

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
    c.connect((args.host,int(args.port)))

    # first message client sends to server is handshake message. client sends username and password and gets token back

    #test
    c.sendshort("Hi")

    #c.loop()
    c.stop()
