from Client.protocol import Client
import logging
FORMAT='%(asctime)s %(message)s'
logging.basicConfig(level=logging.INFO,format=FORMAT)


if __name__ == '__main__':

    c = Client()
    c.connect(('127.0.0.1',7777))

    #test
    c.sendshort("Hi")

    c.loop()
    c.stop()
