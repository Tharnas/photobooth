#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2018  Balthasar Reuter <photobooth at re - web dot eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging
from time import sleep
from RF24 import *

from .. import StateMachine
from ..Threading import Workers


class RemoteButton:

    def __init__(self, config, comm):

        super().__init__()

        self._comm = comm
        self._is_trigger = False

        self.radio = RF24(22, 0);
        self.radio.begin()
        self.radio.openReadingPipe(1,0xE8E8F0F0E1)
        self.radio.startListening()
        
        
    def run(self):
        
        
        while True:
            #for state in self._comm.iter(Workers.REMOTEBUTTON):
            job = self._comm.recv(Workers.REMOTEBUTTON)
            if (job):
                self.handleState(job)
            
            #logging.info("check radio")
            
            if (self.radio.available()):
                receive_payload = self.radio.read(4)
                logging.info("data received: {}".format('-'.join('{:02x}'.format(x) for x in receive_payload)))
                if (receive_payload[0] == 0x01 and receive_payload[1] == 0x02 and receive_payload[2] == 0x03 and receive_payload[3] == 0x04):
                    logging.info("Start to trigger")
                    self.trigger()
                else:
                    logging.info("Did not trigger because data did not match")
                    sleep(1/100)
            else:
                sleep(1/100)
        return True
    
    
    def handleState(self, state):

        if isinstance(state, StateMachine.IdleState):
            self.enableTrigger()
        elif isinstance(state, StateMachine.GreeterState):
            self.disableTrigger()
            
    
    def trigger(self):
        logging.info("try to trigger")

        if self._is_trigger:
            self.disableTrigger()
            self._comm.send(Workers.MASTER, StateMachine.GpioEvent('trigger'))
            logging.info("triggered")


    def enableTrigger(self):
        logging.info("enable trigger")
        self._is_trigger = True


    def disableTrigger(self):
        logging.info("disable trigger")
        self._is_trigger = False

