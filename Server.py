#! /usr/bin/env python

import socket
import sys, traceback
import threading
import thread
import select
SOCKET_LIST=[]
TO_BE_SENT=[]
SENT_BY={}
class Server(threading.Thread):

    def init(self):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # AF_INET is the internet address family for IPv4, SOCK_STREAM is the socket type for TCP
        self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.bind(('',5545))

        # The listen() call indicates a readiness to accept client connection requests. 
        # It transforms an active socket into a passive socket
        self.sock.listen(2)
        SOCKET_LIST.append(self.sock)
        print ("Server started on port 5545")

    def run(self):
        while 1:
            # The select() function monitors all the client sockets and the server socket for readable activity. 
            # If any of the client socket is readable then it means that one of the chat client has send a message
            read,write,err=select.select(SOCKET_LIST,[],[],0)     
            for sock in read:
                if sock==self.sock:      

                    # The accept() call is used by a server to accept a connection request from a client.
                    # When a connection is available, the socket created is ready for use to read data from the process that requested the connection
                    sockfd,addr=self.sock.accept() # scokfd is a socket descriptor returned by the socket function
                    # addr contains the local IP address and port
                    # print (str(addr))
                    SOCKET_LIST.append(sockfd)
                    # print (SOCKET_LIST[len(SOCKET_LIST)-1])
                else:
                    try:
                        # Writing the messages into s
                        s=sock.recv(1024)
                        if s=='':
                            print(str(sock.getpeername())  )                          
                            continue
                        else:
                            # Appending the message to TO_BE_SENT
                            TO_BE_SENT.append(s)  
                            SENT_BY[s]=(str(sock.getpeername()))
                    except:
                        print (str(sock.getpeername()) )                   
                    
            
class handle_connections(threading.Thread):
    def run(self):        
        while 1:
            read,write,err=select.select([],SOCKET_LIST,[],0)
            for items in TO_BE_SENT:
                for s in write:
                    try:
                        if(str(s.getpeername()) == SENT_BY[items]):
                        	print("Ignoring %s"%(str(s.getpeername())))
                        	continue
                        print ("Sending to %s"%(str(s.getpeername())))
                        s.send(items)                                             
                        
                    except:
                        traceback.print_exc(file=sys.stdout)
                TO_BE_SENT.remove(items)   
                del(SENT_BY[items])              
                


if __name__=='__main__':
    srv=Server()
    srv.init()
    srv.start()
    print (SOCKET_LIST)
    handle=handle_connections()    
    handle.start()   

