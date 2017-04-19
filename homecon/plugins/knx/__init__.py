#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import knxpy

from ... import core

class Knx(core.plugin.Plugin):
    """
    Communicate with an EIB-KNX home automation system through an ethernet
    interface

    """

    def initialize(self):

        core.states.add('knx/settings/interface/ip', value='192.168.1.1', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':'', 'private':True})
        core.states.add('knx/settings/interface/port', value='3671', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':'', 'private':True})

        core.states.add('knx/dummy', config={'type': 'number', 'quantity':'', 'unit':'','label':'', 'description':'', 'private':True})

        self.connected = False

        # connect
        self._loop.create_task(self.connect())

        logging.debug('KNX plugin Initialized')
    

    async def connect(self):

        async def callback(msg):
            states = self.get_states_ga_read(ga=knxpy.util.decode_ga(msg.dst_addr))
            for state in states:
                knx_dpt = None
                if 'knx_dpt' in state.config:
                    knx_dpt = state.config['knx_dpt']
                    data = knxpy.util.decode_dpt(msg.data,str(knx_dpt))

                    state.set(data,source=self)


        if not core.states['knx/settings/interface/ip'].value is None and not core.states['knx/settings/interface/port'].value is None:
            ip = core.states['knx/settings/interface/ip'].value
            port = int(core.states['knx/settings/interface/port'].value)
            try:
                self.tunnel = knxpy.asyncip.KNXIPTunnel(ip,port,loop=self._loop,callback=callback)
                await self.tunnel.connect()  # FIXME if a wrong address is suppied, connect freezes

                self.connected = True
                logging.debug('Connected to a KNX interface at {}'.format(ip))

            except:
                logging.error('Could not connect with the KNX ip interface on {}:{}'.format(ip,port))


    def get_states_ga_write(self,ga=None):
        """
        Get states with a knx_ga_write config key

        Parameters
        ----------
        ga : string, optional
            A knx group address

        """
        
        return self._get_states_ga_xxx(ga=ga,sub='write')


    def get_states_ga_read(self,ga=None):
        """
        Get states with a knx_ga_write config key

        Parameters
        ----------
        ga : string, optional
            A knx group address

        """
        
        return self._get_states_ga_xxx(ga=ga,sub='read')


    def _get_states_ga_xxx(self,ga=None,sub='write'):
        """
        Get states with a knx_ga_read config key

        Parameters
        ----------
        ga : string, optional
            A knx group address
        sub : string
            'write'/'read'

        """
        
        states = []

        if ga is None:
            for state in core.states.values():
                if 'knx_ga_{}'.format(sub) in state.config:
                    states.append(state)
        else:
            for state in core.states.values():
                if 'knx_ga_{}'.format(sub) in state.config and state.config['knx_ga_{}'.format(sub)] == ga:
                    states.append(state)

        return states

    def listen_state_changed(self,event):
        state = event.data['state']

        if state.path == 'knx/settings/interface/ip' or state.path == 'knx/settings/interface/port':
            self.connect()
        

        elif 'knx_ga_write' in state.config and 'knx_dpt' in state.config:
            if not event.source == self:
                self.tunnel.group_write(str(state.config['knx_ga_write']),state.value,str(state.config['knx_dpt']))
                logging.debug('{} changed, written {} to knx group address: {}'.format(state.path,state.value,state.config['knx_ga_write']))
        




