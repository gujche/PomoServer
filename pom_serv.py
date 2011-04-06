#! /usr/bin/python

import SocketServer
import socket
import threading
import time
import sys
from task import Task
from pom_msg import *
from the_work import work_it
import loader

#----------------CONFIG FILE STUFF----------------
PORT = 12345
HOST = "localhost"
filename = 'first.dat'
work_block = 20
play_block = 20
#-------------------------------------------------

class PomHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = fromStr(self.request.recv(1024))
        # self.request.send(response)
        self.request.close()
        self.server.code = data.getCode()
        if data.getCode() == 0:
            print 'Shutting down Pom Server...'
            self.server.shutdown()

    def finish(self):
        self.__done = True

class PServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    daemon_threads = True
    code = RUN

if __name__ == "__main__":
    # configure server
    server = PServer((HOST, PORT), PomHandler)

    # begin listening
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()

    # configure Pomodoro functions
    q = loader.loadFile(filename)
    in_time = time.time()
    isPlay = False
    t_block = work_block

    while threading.active_count() > 1:
        if server.code == DONE: #if server.code in [set] use me!
            tasq = work_it(q, server.code, in_time)
            print 'Starting play time...'
            isPlay = True
            t_block = play_block
            in_time = time.time()
            server.code = RUN
        elif server.code == RUN:
            if int(time.time() - in_time) > t_block:
                if isPlay == False:
                    tasq = work_it(q, DONE) # RUN OUT OF TASKS?
                    print 'Starting play time...'
                    isPlay = True
                    t_block = play_block
                    in_time = time.time()
                else:
                    print 'Play Time Over...'
                    print 'Begin ' + q[0].name
                    isPlay = False
                    t_block = work_block
                    in_time = time.time()
        time.sleep(0.1)
        
    sys.exit(0)

# requires a the_work wrapper function that returns the server to the Run state
