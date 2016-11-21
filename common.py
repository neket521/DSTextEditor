# TCP related constants -------------------------------------------------------
DEFAULT_SERVER_PORT = 7777
DEFAULT_SERVER_INET_ADDR = '127.0.0.1'

# Requests --------------------------------------------------------------------
__REQ_PUBLISH = '1'
__REQ_LAST = '2'
__REQ_GET = '3'
__REQ_GET_N_LAST = '4'
__CTR_MSGS = { __REQ_GET:'Get message by id',
               __REQ_LAST:'Get iDs of last N messages',
               __REQ_PUBLISH:'Publish new message',
               __REQ_GET_N_LAST:'Get last N messages'
              }
# Responses--------------------------------------------------------------------
__RSP_OK = '0'
__RSP_BADFORMAT = '1'
__RSP_MSGNOTFOUND = '2'
__RSP_UNKNCONTROL = '3'
__RSP_ERRTRANSM = '4'
__RSP_CANT_CONNECT = '5'
__ERR_MSGS = { __RSP_OK:'No Error',
               __RSP_BADFORMAT:'Malformed message',
               __RSP_MSGNOTFOUND:'Message not found by iD',
               __RSP_UNKNCONTROL:'Unknown control code',
               __RSP_ERRTRANSM:'Transmission Error',
               __RSP_CANT_CONNECT:'Can\'t connect to server'
               }
# Field separator for sending multiple values ---------------------------------
__MSG_FIELD_SEP = ':'