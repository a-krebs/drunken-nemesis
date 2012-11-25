#################################################################################
#  This file is part of The AI Sandbox.
#
#  Copyright (c) 2007-2012, AiGameDev.com
#
#  Credits:         See the PEOPLE file in the base directory.
#  License:         This software may be used for your own personal research
#                   and education only.  For details, see the LICENSING file.
################################################################################

import sys
import os
print os.getcwd()

from inspect import isclass
import importlib
import exceptions
import time
import socket
import json
import gc

import api
from api import commands
from api import gameinfo
from api import handshaking

class DisconnectError(Exception):
    pass

class NetworkClient(object):
    def __init__(self, conn, commanderCls):
        super(NetworkClient, self).__init__()
        self.conn = conn
        self.inputBuffer = ''
        self.commander = commanderCls()
        # set the socket connection as non-blocking
        self.conn.settimeout(0.0)

    def performHandshaking(self):
        # wait for the server to send its handshaking message
        # TODO: timeout after 10 seconds
        message = self.readLine()
        assert message == '<connect>','Received unexpected message from the server. Expected connect message.'

        connectServerJson = self.readLine()
        connectServer = json.loads(connectServerJson, object_hook = handshaking.fromJSON)
        if not connectServer.validate():
            raise DisconnectError()

        # send the handshaking message
        connectClient = handshaking.ConnectClient(self.commander.name, "python")
        connectClientJson =  json.dumps(connectClient, default = handshaking.toJSON)
        message = "<connect>\n{}\n".format(connectClientJson)
        self.conn.send(message)

    def sendReady(self):
        message = "<ready>\n"
        self.conn.send(message)

    def sendCommands(self):
        for command in self.commander.commandQueue:
            commandJson =  json.dumps(command, default = commands.toJSON)
            message = "<command>\n{}\n".format(commandJson)
            # print message
            self.conn.send(message)
        self.commander.clearCommandQueue()

    def initializeCommanderGameData(self, levelInfoJson, gameInfoJson):
        levelInfo = json.loads(levelInfoJson, object_hook=gameinfo.fromJSON)
        gameInfo = json.loads(gameInfoJson, object_hook=gameinfo.fromJSON)
        gameinfo.fixupGameInfoReferences(gameInfo)
        self.commander.level = levelInfo
        self.commander.game = gameInfo

    def updateCommanderGameData(self, gameInfoJson):
        gameInfo = json.loads(gameInfoJson, object_hook=gameinfo.fromJSON)
        gameinfo.mergeGameInfo(self.commander.game, gameInfo)

    def run(self):
        self.performHandshaking()

        initialized = False
        tickRequired = False

        while True:
            while True:
                message = self.readLineNonBlocking()
                if message == '':
                    break
                elif message == '<initialize>':
                    assert not initialized, 'Unexpected initialize message {}'.format(message)
                    levelInfoJson = self.readLine()
                    gameInfoJson = self.readLine()
                    self.initializeCommanderGameData(levelInfoJson, gameInfoJson)
                    self.commander.initialize()
                    self.sendReady()
                    initialized = True

                elif message == '<tick>':
                    assert initialized, 'Unexpected message {} while waiting for initialize'.format(message)
                    gameInfoJson = self.readLine()
                    self.updateCommanderGameData(gameInfoJson)
                    tickRequired = True

                elif message == '<shutdown>':
                    assert initialized, 'Unexpected message {} while waiting for initialize'.format(message)
                    self.commander.shutdown()
                    return

                else:
                    assert False, 'Unknown message received: {}'.format(message)

            if tickRequired:
                self.commander.tick()
                self.sendCommands()
                tickRequired = False
            else:
                time.sleep(0.0001)
 
            # gc.collect()
 

    def readLineNonBlocking(self):
        try:
            while True:
                data = self.conn.recv(4096)
                self.inputBuffer += data
        except socket.error, msg:
            pass
        line, sep, self.inputBuffer = self.inputBuffer.partition('\n')
        if sep == '':
            # if there is no newline character, leave all of the contents in the buffer
            # and return an empty string
            self.inputBuffer = line
            line = ''
        return line

    def readLine(self):
        while True:
            line = self.readLineNonBlocking()
            if line != '':
                return line


def getCommander(name):
    """Given a Commander name, import the module and return the class
    object so it can be instantiated for the competition."""
    filename, _, classname = name.rpartition('.')
    try:
        module = importlib.import_module(filename)
    except ImportError as e:
        print >> sys.stderr,  "ERROR: While importing '%s', %s." % (name, e)
        return

    for c in dir(module):
        # Check if this Commander was explicitly exported in the module.
        if hasattr(module, '__all__') and not c in module.__all__: continue
        # Discard private classes or the base class.
        if c.startswith('__') or c == 'Commander': continue
        # Match the class by the specified sub-name.
        if classname is not None and classname not in c: continue

        # Now check it's the correct derived class...
        cls = getattr(module, c)
        try:
            if isclass(cls) and issubclass(cls, api.Commander):
                return cls
        except TypeError:
            pass

    if not found:
        print 'Unable to find commander {}'.format(request)
        assert False


def main(args):
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('commander')
    args, _ = parser.parse_known_args()

    commanderCls = getCommander(args.commander)
    if not commanderCls:
        print >> sys.stderr, "Unable to find commander {}".format(args.commander)
        return

    HOST, PORT = 'localhost', 41041
    print 'Connecting to {}:{}'.format(HOST, PORT)
    for i in range(100):
        try:
            s = socket.create_connection((HOST, PORT))
            print 'Connected!'

            wrapper = NetworkClient(s, commanderCls)
            wrapper.run()
            break;

        except socket.error, msg:
            pass    
    
    else:
        print >> sys.stderr, "Unable to connect to game server at {}:{}".format(HOST, PORT)        


from traceback import extract_tb

def format(tb, limit = None):
    extracted_list = extract_tb(tb)
    list = []
    for filename, lineno, name, line in extracted_list:
        item = '%s(%d): error in %s' % (filename,lineno,name)
        if line:
            item = item + '\n\t%s' % line.strip()
        else:
            item = item + '.'
        list.append(item)
    return list


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception as e:
        print str(e)
        tb_list = format(sys.exc_info()[2])
        for s in tb_list:
            print s
        raise
