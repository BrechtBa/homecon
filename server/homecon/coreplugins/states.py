#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from .. import core
from .authentication import jwt_decode

class States(core.plugin.Plugin):
    """
    Class to control the HomeCon states
    
    Each 'state' in the building should be reflected by a HomeCon state. This 
    can be the status of a light (on/off), the temperature in a room, the solar 
    irradiation, ...
    
    A state is identified by a string, its path. The predefined HomeCon States are 
    structured as if they were actual paths to folders on a unix system, using
    slashes (:code`/`). e.g. :code`settings/latitude`.
    
    Unlike a folder structure, the paths remain simple strings so 
    'parent folders' do not need to exists.
    
    The format is not manatory, any characters can be used. However, when using
    this format, parent or child states can be retrieved are available and for 
    dependent expressions some regular expression syntax can be used.
    
    """

    def initialize(self):


        # add settings states
        core.states.add('settings/location/latitude', config={'type': 'number', 'quantity':'angle', 'unit':'deg','label':'latitude', 'description':'HomeCon latitude'})
        core.states.add('settings/location/longitude',config={'type': 'number', 'quantity':'angle', 'unit':'deg','label':'longitude','description':'HomeCon longitude'})
        core.states.add('settings/location/elevation',config={'type': 'number', 'quantity':'height','unit':'m',  'label':'elevation','description':'HomeCon elevation'})
        core.states.add('settings/location/timezone', config={'type': 'string', 'quantity':'',      'unit':'',   'label':'time zone','description':'HomeCon time zone'})


        logging.debug('States plugin Initialized')

    def get(self,path):
        """
        gets a state given its path
        
        Parameters
        ----------
        path : string
            the state path

        Returns
        -------
        state : State
            the state or :code`None`if the state is unknown

        """

        if path in core.states:
            return core.states[path]
        else:
            logging.error('State {} is not defined'.format(path))
            return None

    def list(self):
        """
        Returns a list of states which can be edited
        """

        stateslist = []
        for state in core.states.values():
            stateslist.append({'path':state.path,'config':sorted([{'key':key,'value':val} for key,val in state.config.items()],key=lambda x:x['key'])})

        newlist = sorted(stateslist, key=lambda k: k['path'])

        return newlist


    def listen_list_states(self,event):
        if event.type == 'list_states':

            core.event.fire('send_to',{'event':'list_states', 'path':'', 'value':self.list(), 'clients':[event.client]})


    def listen_add_state(self,event):
        state = core.states.add(event.data['path'],config=event.data['config'])

        if state:
            core.event.fire('state_added',{'state':state})
            core.event.fire('send_to',{'event':'list_states', 'path':'', 'value':self.list(), 'clients':[event.client]})


    def listen_edit_state(self,event):
        if event.data['path'] in core.states:

            state = core.states[event.data['path']]

            config = dict(state.config)
            for key,val in event.data['config'].items():
                config[key] = val

            state.config = config

            core.event.fire('send_to',{'event':'list_states', 'path':'', 'value':self.list(), 'clients':[event.client]})


    def listen_state_config(self,event):
        if event.data['path'] in core.states:

            state = core.states[event.data['path']]

            if not 'value' in event.data:
                core.event.fire('send_to',{'event':'state_config', 'path':state.path, 'value':state.config, 'clients':[event.client]})

            else:
                logger.warning('listen_state_config, edit state config :' + state.path)
                #config = dict(state.config)
                #for key,val in event.data['config'].items():
                #    config[key] = val

                #state.config = config
                #self.fire('send_to',{'event':'state_config', 'path':state.path, 'value':state.config, 'clients':[event.client]})
                #self.fire('send_to',{'event':'list_states', 'path':'', 'value':self.list(), 'clients':[event.client]})


    def listen_state_changed(self,event):
        core.event.fire('send',{'event':'state', 'path':event.data['state'].path, 'value':event.data['state'].value, 'readusers':event.data['state'].config['readusers'], 'readgroups':event.data['state'].config['readgroups']},source=self)


    def listen_state(self,event):
        
        if 'path' in event.data:
            # get or set a state
            state = self.get(event.data['path'])

            if not state is None:
                tokenpayload = jwt_decode(event.data['token'])

                if 'value' in event.data:
                    # set
                    permitted = False
                    if tokenpayload and tokenpayload['userid'] in state.config['writeusers']:
                        permitted = True
                    else:
                        for g in tokenpayload['groupids']:
                            if g in state.config['writegroups']:
                                permitted = True
                                break

                    if permitted:

                        value = event.data['value']
                        if 'type' in state.config and state.config['type'] == 'number':
                            value = float(value)

                        state.set(value,source=event.source)

                    else:
                        logging.warning('User {} on client {} attempted to change the value of {} but is not permitted'.format(tokenpayload['userid'],event.client.address,state.path))

                else:
                    # get
                    permitted = False
                    if tokenpayload and tokenpayload['userid'] in state.config['readusers']:
                        permitted = True
                    elif tokenpayload:
                        for g in tokenpayload['groupids']:
                            if g in state.config['readgroups']:
                                permitted = True
                                break

                    if permitted:
                        core.event.fire('send_to',{'event':'state', 'path':state.path, 'value':state.value, 'clients':[event.client]})
                    else:
                        logging.warning('User {} attempted to change the value of {} but is not permitted'.format(tokenpayload['userid'],state.path))


    def listen_send_states_to(self,event):
        for client in event.data['clients']:
            tokenpayload = jwt_decode(event.data['token'])

            for state in core.states.values():
                permitted = False
                if tokenpayload and tokenpayload['userid'] in state.config['readusers']:
                    permitted = True
                elif tokenpayload:
                    for g in tokenpayload['groupids']:
                        if g in state.config['readgroups']:
                            permitted = True
                            break

                if permitted:
                    core.event.fire('send_to',{'event':'state', 'path':state.path, 'value':state.value, 'clients':[client]})




