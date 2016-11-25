# TCP related constants -------------------------------------------------------
DEFAULT_SERVER_PORT = 7777
DEFAULT_SERVER_INET_ADDR = '127.0.0.1'

# Requests --------------------------------------------------------------------
REQ_SEND = '1'
REQ_GET = '2'
REQ_AUTH = '3'
REQ_GETLF = '4' #get list of files
REQ_GETF = '5' #get file by name
REQ_SP = '6' #send line number
# Responses--------------------------------------------------------------------
RSP_OK_SEND = '0'
RSP_OK_GET = '1'
RSP_OK_AUTH = '2'
RSP_BADFORMAT = '3'
RSP_MSGNOTFOUND = '4'
RSP_UNKNCONTROL = '5'
RSP_ERRTRANSM = '6'
RSP_CANT_CONNECT = '7'
RSP_NOTIFY = '8'
RSP_ERR_AUTH = '9'
RSP_OK_GETLF = '10'
RSP_OK_GETF = '11'
RSP_OK_SP = '12'
# Field separator for sending multiple values ---------------------------------
MSG_FIELD_SEP = ':'
MSG_SEP = ';'
# Buffer size
DEFAULT_BUFSIZE = 1024
