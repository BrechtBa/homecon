#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import os
import sys
import uuid
import pip
import pyomo.environ as pyomo

from concurrent.futures import ThreadPoolExecutor

from . import event
from . import state
from . import component
from . import database
from . import ws

# the worker thread pool
executor = ThreadPoolExecutor(10)


class Plugins(object):
    """
    a container class for plugins with access to the database

    """
    def __init__(self):

        self._plugins = {}
        self._availableplugins = {}

        self.pluginfolder = 'plugins'

        # objects for all plugins
        self._db_plugins = database.Table(database.db,'plugins',[
            {'name':'name',   'type':'char(255)', 'null': '', 'default':'', 'unique':'UNIQUE'},
            {'name':'package','type':'char(255)', 'null': '', 'default':'', 'unique':''},
            {'name':'core',   'type':'int',  'null': '',  'default':'0',  'unique':''},
            {'name':'active', 'type':'int',  'null': '',  'default':'0',  'unique':''},
        ]) 
        

        # check the core plugins
        result = self._db_plugins.GET()
        _list = []
        for db_entry in result:
            _list.append(db_entry['name'])

        if not 'states' in _list:
            self._db_plugins.POST(name='states',core=1,active=1,package='homecon.plugins')
        if not 'components' in _list:
            self._db_plugins.POST(name='components',core=1,active=1,package='homecon.plugins')
        if not 'plugins' in _list:
            self._db_plugins.POST(name='plugins',core=1,active=1,package='homecon.plugins')
        if not 'authentication' in _list:
            self._db_plugins.POST(name='authentication',core=1,active=1,package='homecon.plugins')
        if not 'pages' in _list:
            self._db_plugins.POST(name='pages',core=1,active=1,package='homecon.plugins')
        if not 'schedules' in _list:
            self._db_plugins.POST(name='schedules',core=1,active=1,package='homecon.plugins')
        if not 'actions' in _list:
            self._db_plugins.POST(name='actions',core=1,active=1,package='homecon.plugins')
        if not 'measurements' in _list:
            self._db_plugins.POST(name='measurements',core=1,active=1,package='homecon.plugins')
        if not 'weather' in _list:
            self._db_plugins.POST(name='weather',core=1,active=1,package='homecon.plugins')
        if not 'building' in _list:
            self._db_plugins.POST(name='building',core=1,active=1,package='homecon.plugins')
        if not 'mpc' in _list:
            self._db_plugins.POST(name='mpc',core=1,active=1,package='homecon.plugins')
        if not 'shading' in _list:
            self._db_plugins.POST(name='shading',core=1,active=1,package='homecon.plugins')


        # check the included plugins
        if not 'knx' in _list:
            self._db_plugins.POST(name='knx',core=0,active=0,package='homecon.plugins')
        if not 'darksky' in _list:
            self._db_plugins.POST(name='darksky',core=0,active=0,package='homecon.plugins')
        if not 'flukso' in _list:
            self._db_plugins.POST(name='flukso',core=0,active=0,package='homecon.plugins')


        # list all plugins
        result = self._db_plugins.GET()
        for db_entry in result:
            self._availableplugins[db_entry['name']] = {'name':db_entry['name'],'id':db_entry['id'],'core':db_entry['core'] == 1,'package':db_entry['package'],'active':db_entry['active'] == 1}


    def start_import(self):
        """
        Import and start all core plugins
        Called once during homecon initialization

        """

        # import all active plugins
        classlist = []

        # sorted pluginlist respect the loading/installation order
        _availableplugins = sorted(self._availableplugins.values(),key=lambda x:x['id'])

        for plugin in _availableplugins:
            if plugin['active']:
                classlist.append( self._import(plugin['name'],package=plugin['package']) )

        self._classlist = classlist


    def start_activate(self):
        plugins
        # activate all plugins
        for cls in self._classlist:
            self._activate(cls)

        self._classlist = []


    def install(self,url):
        """
        Download a plugin from a url

        """

        try:
            os.mkdir(os.path.join(sys.prefix,'downloads'))
        except:
            pass


        # download the package zip
        fname = os.path.split(url)[-1].split('#')[0]

        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(os.path.join(sys.prefix,'var','tmp','homecon',fname), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f) 

                # install using pip
                pip.main(['install', os.path.join(sys.prefix,'var','tmp','homecon',fname)])

                # add the plugin to the database and available plugins list
                pluginname = fname.split('-')[0]
                self._db_plugins.POST(name=pluginname,core=0,active=0,package='')

                result = self._db_plugins.GET(name=pluginname)
                for db_entry in result:
                    self._availableplugins[db_entry['name']] = {'name':db_entry['name'],'id':db_entry['id'],'core':db_entry['core'] == 1,'package':db_entry['package'],'active':db_entry['active'] == 1}


                return True

        return False


    def uninstall(self,name):
        """
        delete a plugin from the availableplugins list and the hard disk 

        Parameters
        ----------
        name: string
            The module name of the plugin

        """
        return False


    def activate(self,name):
        """
        activate a plugin

        Parameters
        ----------
        name: string
            The module name of the plugin

        """
        # check if the name is in the available plugins
        if name in self._availableplugins:
    
            cls = self._import(name,package=self._availableplugins[name]['package'])
            self._activate(cls)


    def deactivate(self,name):
        """
        deactivate a plugin

        Parameters
        ----------
        name: string
            The module name of the plugin

        """

        if name in self._availableplugins and name in self._plugins and not self._availableplugins[name]['core']:

            # FIXME stop the plugin
            self._plugins[name].stop()

            # remove the pluging from the pluginslist
            del self._plugins[name]

            # set the plugin as not active in the list and database
            self._availableplugins[name]['active'] = False
            self._db_plugins.PUT(active=0, where='name=\'{}\''.format(name))

            return True

        else:
            return False


    def read_info(self,name):
        """
        Reads the plugin info file from disk

        Parameters
        ----------
        name: string
            The module name of the plugin

        """

        try:
            infofile = os.path.join( os.path.dirname(os.path.realpath(__file__)) ,'..',self.pluginfolder,name,'info')
            with open(infofile,'r') as f:
                return f.read()
        except:
            return ''
        

    @property
    def availableplugins(self):
        return self._availableplugins


    @property
    def optionalplugins(self):
        _optionalplugins = {plugin['name']: plugin for plugin in self._availableplugins.values() if not plugin['core']}

        return _optionalplugins


    def _import(self,name,package=None):
        """
        Imports a plugin module

        this attempts to load the plugin with the correct format by name from
        the plugins folder

        Parameters
        ----------
        name: string
            The module name of the plugin
    
        package: string
            Package where to find the plugin, defaults to the default pluginfolder

        returns
        -------
        pluginclass: class
            The plugin class if defined in the module otherwise ``None``

        """

        if package is None or package == '':
            pluginmodule = __import__(name, fromlist=[name])
        else:
            pluginmodule = __import__('{}.{}'.format(package,name), fromlist=[name])

        pluginclass = None
        pluginclassname = name.capitalize()
        if pluginclassname in dir(pluginmodule):
            pluginclass = getattr(pluginmodule, pluginclassname)
        
        return pluginclass


    def _activate(self,pluginclass):
        """
        activates a plugin

        Parameters
        ----------
        pluginclass: class
            The plugin class

        """

        name = pluginclass.__name__.lower()
        plugin = pluginclass()

        self._availableplugins[name]['active'] = True
        self._db_plugins.PUT(active=1, where='name=\'{}\''.format(name))
        self._plugins[name] = plugin


    def __getitem__(self,path):
        return self._plugins[path]


    def __iter__(self):
        return iter(self._plugins)


    def __contains__(self,path):
        return path in self._plugins


    def keys(self):
        return self._plugins.keys()


    def items(self):
        return self._plugins.items()


    def values(self):
        return self._plugins.values()




class Plugin(object):
    """
    A class for defining plugins with listener methods

    Notes
    -----
    A plugin can not send events to itself through the fire / listen methods

    Examples
    --------
    .. code-block::
        def listen_someevent(self,event):
            self.do_something(event)

        def listen_someotherevent(self,event):
            self.do_somethingelse(event)

    """


    def __init__(self):
        """
        Initialize a plugin instance
        
        Parameters
        ---------
        queue : event queue
            the main homecon event queue
            
        states : homecon.core.states.States
            the main homecon states object
            
        components : homecon.core.components.Components
            the main homecon components object
            
        """

        self._queue = event.queue
        self._states = state.states
        self._components = component.components

        self._loop = asyncio.get_event_loop()

        self.config_keys = []
        self.ocp_variables = {}

        self._get_listeners()

        self.active = True
        self.initialize()


    def _get_listeners(self):
        self.listeners = {}
        for method in dir(self):
            if method.startswith('listen_'):
                event = '_'.join(method.split('_')[1:])
                self.listeners[event] = getattr(self,method)


    def initialize(self):
        """
        Base method runs when the plugin is instantiated
        
        redefine this method in a child class
        """
        pass


    def register_component(self,componentclass):
        self._components.register(componentclass)


    def components(self):
        """
        Redefinable method which should return a list of components defined by the plugin and enables the app to edit the component

        Examples
        --------
        [{
            'name': 'light',
            'properties': ['power'],
            'states': [
                {
                    'path': 'value',    # the final path of a state is prefixed with the component path ex. living/light1/value
                    'defaultconfig': {         # values listed here will be defaults
                        'label': 'light',
                        'quantity': 'boolean',
                        'unit' : ''
                    },
                    'fixedconfig': {         # values listed here will not be changeable
                        'type': bool
                    },
                },
            ]
        },]

        """

        return []


    def fire(self,event_type,data,source=None,client=None):
        """
        Add the event to the que
        
        Parameters
        ----------
        event_type : string
            the event type

        data : dict
            the data describing the event
        
        source : string
            the source of the event
            
        """

        if source==None:
            source = self

        event.fire(event_type,data,source,client)


    def stop(self):
        """
        Base method to stop the plugin

        Called when a plugin is deactivated
        """
        self.active = False


    def create_ocp_variables(self,model):
        """
        Base method to create ocp model variables

        Called before the ocp constraints are created
        """
        pass


    def create_ocp_constraints(self,model):
        """
        Base method to create ocp model constraints

        Called before the ocp is solved
        """
        pass


    def postprocess_ocp(self,model):
        """
        Base method to retrieve data from the ocp solution

        Called after the ocp is solved
        """
        pass


    def add_ocp_Var(model,localname,*args,**kwargs):
        """
        Adds a variable to a pyomo model and adds it to the local variables dictionary
        
        Parameters
        ----------
        model : pyomo.environ.ConcreteModel
            The optimization model.
            
        localname : str
            A local name to reference the variable
            
        *args : 
            positional parameters passed to pyomo.environ.Var
            
        *args : 
            keyword parameters passed to pyomo.environ.Var
            
        """
        
        var = pyomo.Var(*args,**kwargs)
        self.ocp_variables[localname] = var
        setattr(model,'{}_{}'.format(self.__class__.__name__.lower(),localname),var)
        

    def add_ocp_Param(model,localname,*args,**kwargs):
        """
        Adds a parameter to a pyomo model and adds it to the local variables dictionary
        
        Parameters
        ----------
        model : pyomo.environ.ConcreteModel
            The optimization model.
            
        localname : str
            A local name to reference the variable
            
        *args : 
            positional parameters passed to pyomo.environ.Param
            
        *args : 
            keyword parameters passed to pyomo.environ.Param
            
        """
        
        var = pyomo.Param(*args,**kwargs)
        self.ocp_variables[localname] = var
        setattr(model,'{}_{}'.format(self.__class__.__name__.lower(),localname),var)
        

    def add_ocp_Constraint(model,localname,*args,**kwargs):
        """
        Adds a constraint to a pyomo model
        
        Parameters
        ----------
        model : pyomo.environ.ConcreteModel
            The optimization model.
            
        localname : str
            A local name to reference the constraint
            
        *args : 
            positional parameters passed to pyomo.environ.Param
            
        *args : 
            keyword parameters passed to pyomo.environ.Param
            
        """
        
        var = pyomo.Constr(*args,**kwargs)
        setattr(model,'constraint_{}_{}'.format(self.__class__.__name__.lower(),localname),var)


    def schedule_callback(self,callback,**kwargs):
        """
        Shedule a callback tu run at regular intervals
        """
        # FIXME, implement
        pass


    def _listen(self,event):
        """
        Base listener method called when an event is taken from the queue
        
        Parameters
        ----------
        event : Event
            an Event instance
            
        Notes
        -----
        Source checking to avoid infinite loops needs to be done in the plugin
        listener method

        """

        if event.type in self.listeners:
            #executor.submit(self.listeners[event.type], event)
            #asyncio.ensure_future(self._loop.run_in_executor(executor, self.listeners[event.type], event))
            self.listeners[event.type](event)


    def __getitem__(self,path):
        return None

    def __iter__(self):
        return iter([])

    def __contains__(self,path):
        return False

    def keys(self):
        return []

    def items(self):
        return []

    def values(self):
        return []




class ObjectPlugin(Plugin):
    """
    A plugin including an object list and usefull listeners
    
    objectclass and objectname must be defined in a child class

    """

    objectclass = state.State
    objectname = 'state'

    def __init__(self):


        self._objects_container = self.objectclass.container
        self._objects_db = self.objectclass.db_table

        # get all objects from the database
        result = self.objectclass.db_table.GET()
        for db_entry in result:
            self.objectclass(db_entry['path'],db_entry=db_entry)


        # add listener methods
        def listen_add_object(cls, event):
            """
            add

            """
            if 'path' in event.data:
                path = event.data['path']
            else:
                path = str(uuid.uuid4())

            if 'config' in event.data:
                config = event.data['config']
            else:
                config = None

            if 'value' in event.data:
                value = event.data['value']
            else:
                value = None

            obj = self.objectclass(path,config=config,value=value)

            if obj:
                self.fire('{}_added'.format(self.objectname),{self.objectname: obj})
                ws.websocket.send({'event':'list_{}s'.format(self.objectname), 'path':'', 'value':self.list()})

        def listen_delete_object(cls,event):
            """
            delete

            """
            if 'path' in event.data:
                if event.data['path'] in self:

                    obj = self[event.data['path']]
                    obj.delete()

                    logging.debug('deleted {} {}'.format(self.objectname.capitalize(), event.data['path']))

                    ws.websocket.send({'event':'list_{}s'.format(self.objectname), 'path':'', 'value':self.list()})

                else:
                    logging.error('{} does not exist {}'.format(self.objectname.capitalize(),event.data['path']))


        def listen_list_objects(cls,event):
            """
            list

            """
            if 'path' in event.data:
                filt = event.data['path']
            else:
                filt = None

            ws.websocket.send({'event':'list_{}s'.format(self.objectname), 'path':event.data['path'], 'value':self.list(filter=filt)}, clients=[event.client])


        def listen_object(cls,event):
            """
            get or set

            """
            if 'path' in event.data:
                if event.data['path'] in self:
                    # get or set
                    obj = self[event.data['path']]

                    if 'value' in event.data:
                        # set
                        if isinstance(event.data['value'], dict):
                            value = dict(obj.value)
                            for key,val in event.data['value'].items():
                                value[key] = val
                        else:
                            value = event.data['value']

                        obj.set(value,source=event.source)

                    else:
                        # get
                        ws.websocket.send({'event':self.objectname, 'path':event.data['path'], 'value':obj.value}, clients=[event.client])

                else:
                    logging.error('{} does not exist {}'.format(self.objectname.capitalize(), event.data['path']))


        setattr(ObjectPlugin, 'listen_add_{}'.format(self.objectname), classmethod(listen_add_object))
        setattr(ObjectPlugin, 'listen_delete_{}'.format(self.objectname), classmethod(listen_delete_object))
        setattr(ObjectPlugin, 'listen_list_{}s'.format(self.objectname), classmethod(listen_list_objects))
        setattr(ObjectPlugin, 'listen_{}'.format(self.objectname), classmethod(listen_object))


        # run the parent init
        super(ObjectPlugin,self).__init__()


    def list(self,filter=None):
        """
        redefine if necessary

        """
        unsortedlist = [obj.serialize() for obj in self.values() if (filter is None or filter=='' or not 'filter' in obj.value or obj.value['filter'] == filter)]
        sortedlist = sorted(unsortedlist, key=lambda obj: obj['path'])
        pathlist = [obj['path'] for obj in sortedlist]

        return pathlist


    def __getitem__(self,path):
        return self._objects_container[path]

    def __iter__(self):
        return iter(self._objects_container)

    def __contains__(self,path):
        return path in self._objects_container

    def keys(self):
        return self._objects_container.keys()

    def items(self):
        return self._objects_container.items()

    def values(self):
        return self._objects_container.values()


# create the plugins container
plugins = None

