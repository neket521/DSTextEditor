from Server.server_main import __info, ___VER,\
    server_main
from common import DEFAULT_SERVER_INET_ADDR,\
    DEFAULT_SERVER_PORT
from argparse import ArgumentParser # Parsing command line arguments
from sys import path,argv
from os.path import abspath, sep
# Main method -----------------------------------------------------------------
if __name__ == '__main__':
    # Find the script absolute path, cut the working directory
    a_path = sep.join(abspath(argv[0]).split(sep)[:-1])
    # Append script working directory into PYTHONPATH
    path.append(a_path)
    # Parsing arguments
    # Parsing arguments
    parser = ArgumentParser(description=__info(),
                            version = ___VER)
    parser.add_argument('-l','--listenaddr', \
                        help='Bind server socket to INET address, '\
                        'defaults to %s' % DEFAULT_SERVER_INET_ADDR, \
                        default=DEFAULT_SERVER_INET_ADDR)
    parser.add_argument('-p','--listenport', \
                        help='Bind server socket to port, '\
                        'defaults to %d' % DEFAULT_SERVER_PORT, \
                        default=DEFAULT_SERVER_PORT)
    args = parser.parse_args()
    # Run server
    server_main(args)