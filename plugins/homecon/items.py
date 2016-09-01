#!/usr/bin/python3
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import logging
import json

import lib.item

logger = logging.getLogger('')



class Items(object):
    def __init__(self,sh,db):
        """
        """
        self._sh = sh
        self._db = db

    def load_items(self):
        """
        loads all items from the database
        """
        pass


    def add_item(self,path,conf={},persist=1,label='',description='',unit=''):
        """
        adds an item to the database and smarthome
        """

        # check if the item parent exists
        split_path = path.split('.')
        parent_path = '.'.join(split_path[:-1])

        if parent_path=='':
            parent = self._sh
        else:
            parent = self._sh.return_item(parent_path)

        if not parent==None:
            # add the item to the database
            success = self._db.add_item(path,json.dumps(conf),persist,label,description,unit)

            if success:
                # add the item to smarthome
                self._add_item_to_smarthome(parent,path,conf)

            else:
                logger.warning('The item {} could not be added to the database'.format(item_path))
        else:
            logger.warning('The item parent {} does not exist'.format(parent_path))


    def _add_item_to_smarthome(self,parent,path,conf):
        """
        Adds a low level item to smarthome.
        Throws an exception when the item parent does not exist

        Arguments:
        smarthome: the smarthome object
            parent:     item, the parent item
            path:       string, the item path
            conf:     dict, key value pairs of conf attributes or child items
        """
        try:
            item = lib.item.Item(self._sh, parent, path, conf)
        except Exception as e:
            logger.error("Item {}: problem creating: {}".format(path, e))

        self._sh.add_item(path, item)

        if parent == self._sh:
            parent._SmartHome__children.append(item)
        else:
            parent._Item__children.append(item)






def update_item(sh,db,conf_string):
    """
    Updates or creates an item from a confuration string and adds it to the database

    Arguments:
    sh: the smarthome object
    db: the database object
    item_conf: string, item confuration string
    
    Example:
    update_item(sh,db,'{"path":"firstfloor.living.window","type":"window","conf": '{"area":"2.1","transmittance":"0.6","children":{"shading":{"transmittance":"0.3","move":{"knx_dpt":"1","knx_send":"2/1/5"}}}}')
    """
    # parse the conf string
    conf = json.loads(conf_string)
    item_path = item_conf['path']
    item_type = item_conf['type']
    item_conf = json.loads(item_conf['conf'])

    # check if the item exists in the database
    db_items = db.GET('item_conf','path={}'.format(item_path))
    db_added = False
    if len(db_items)==0:
        # add the item to the database
        db.POST('item_conf',{'path':json.dumps(item_path),'type':json.dumps(item_type),'conf':json.dumps(item_conf)})
    else:
        db.PUT('item_conf','path={}'.format(item_path),{'path':json.dumps(item_path),'type':json.dumps(item_type),'conf':json.dumps(item_conf)})

    # update the item in smarthome
    update_smarthome_item(sh,item_path,item_type,item_conf)


def delete_item(sh,db,path):
    """
    Deletes an item from a confuration string from smarthome and the database

    Arguments:
    sh: the smarthome object
    db: the database object
    path: string, item path
    
    Example:
    delete_item(sh,db,'firstfloor.living.window')
    """

    # remove the item from the database
    db.DELETE('item_conf','path={}'.format(path))

    # remove the item from smarthome if it exists
    item = sh.return_item(path)
    if not item == None:
        _delete_item(item)





def update_smarthome_item(sh,item_path,item_type,item_conf):
    """
    Adds a items to smarthome from a confuration dictionary
    Throws an exception when the item parent does not exist

    Arguments:
    sh: the smarthome object
    item_path: string
    item_type: string
    item_conf: dict or json string, item confuration  as retrieved from the database
    
    Example:
    create_item(smarthome,'firstfloor.living.window','window','{"area":"2.1","transmittance":"0.6","children":{"shading":{"transmittance":"0.3","children":{"move":{"knx_dpt":"1","knx_send":"2/1/5"}}}}}')    
    """

    # parse item_conf
    if isinstance(item_conf, str):
        item_conf = json.loads(item_conf)
        
    # get the item children confuration
    item_children = {}
    if 'children' in item_conf:
        item_children = item_conf['children']
        del item_conf['children']

    # add the type to conf
    if item_type != '':
        item_conf['type'] = item_type


    # check if the item exists in smarthome
    item = sh.return_item(item_path)
    if not item == None:
        # delete the item and re add it
        # deleting the item is required to reconfure the plugin_method_triggers
        # of all plugins
        _delete_item(item)



    # parse special types
    if item_type == 'heatedzone':
        ########################################################################
        # a heated zone item
        ########################################################################
        # default conf attributes
        default_conf = {'floor_area': '100.0', 'exterior_wall_area':'300.0', 'volume':'250.0'}
        # create the item
        item = _add_item(sh,item_path,conf=default_conf.update(item_conf))


    elif item_type == 'unheatedzone':
        ########################################################################
        # a unheated zone item
        ########################################################################
        # default conf attributes
        default_conf = {'floor_area': '100.0', 'exterior_wall_area':'300.0', 'volume':'250.0'}
        # create the item
        item = _add_item(sh,item_path,conf=default_conf.update(item_conf))


    elif item_type == 'window':
        ########################################################################
        # a window item
        ########################################################################
        # default conf attributes
        default_conf = {'area': '1.0', 'orientation':'0.0', 'tilt':'90.0', 'transmittance':'0.6'}
        # create the item
        item = _add_item(sh,item_path,conf=default_conf.update(item_conf))

        # add a shading item
        child_conf = {}
        if 'shading' in item_children:
            child_conf = item_children['shading']
            
        update_smarthome_item(sh,item_path+'.shading','shading',child_conf)


    elif item_type == 'shading':
        ########################################################################
        # a shading item
        ########################################################################
        # default conf attributes
        default_conf = {'transmittance':'0.3'}
        # create the item
        item = _add_item(sh,item_path,conf=default_conf.update(item_conf))

        # add a move item
        child_conf = {}
        if 'move' in item_children:
            child_conf = item_children['move']

        update_smarthome_item(sh,item_path+'.move','',child_conf)

        # add a stop item
        child_conf = {}
        if 'stop' in item_children:
            child_conf = item_children['stop']

        update_smarthome_item(sh,item_path+'.stop','',child_conf)

        # add a value item
        child_conf = {}
        if 'value' in item_children:
            child_conf = item_children['value']

        update_smarthome_item(sh,item_path+'.value','',child_conf)

        # add a value_status item
        child_conf = {}
        if 'value_status' in item_children:
            child_conf = item_children['value_status']

        update_smarthome_item(sh,item_path+'.value_status','',child_conf)

        # add a auto item
        child_conf = {}
        if 'auto' in item_children:
            child_conf = item_children['auto']

        update_smarthome_item(sh,item_path+'.auto','',child_conf)

        # add a override item
        child_conf = {}
        if 'override' in item_children:
            child_conf = item_children['override']

        update_smarthome_item(sh,item_path+'.override','',child_conf)

        # add a closed item
        child_conf = {}
        if 'closed' in item_children:
            child_conf = item_children['closed']

        update_smarthome_item(sh,item_path+'.closed','',child_conf)

    elif item_type == 'action':
        ########################################################################
        # an alarm item
        ########################################################################
        # default conf attributes
        default_conf = {'item':'[]','delay':'[]','value':'[]'}
        # create the item
        item = _add_item(sh,item_path,conf=default_conf.update(item_conf))


    elif item_type == 'alarm':
        ########################################################################
        # an alarm item
        ########################################################################
        # default conf attributes
        default_conf = {'section':'home'}
        # create the item
        item = _add_item(sh,item_path,conf=default_conf.update(item_conf))

        update_smarthome_item(sh,item_path+'.hour','num',{})
        update_smarthome_item(sh,item_path+'.minute','num',{})

        update_smarthome_item(sh,item_path+'.sunrise','bool',{})
        update_smarthome_item(sh,item_path+'.sunset','bool',{})
        update_smarthome_item(sh,item_path+'.offset','num',{})
        
        update_smarthome_item(sh,item_path+'.mon','bool',{})
        update_smarthome_item(sh,item_path+'.tue','bool',{})
        update_smarthome_item(sh,item_path+'.wed','bool',{})
        update_smarthome_item(sh,item_path+'.thu','bool',{})
        update_smarthome_item(sh,item_path+'.fri','bool',{})
        update_smarthome_item(sh,item_path+'.sat','bool',{})
        update_smarthome_item(sh,item_path+'.sun','bool',{})

        update_smarthome_item(sh,item_path+'.action','action',{})

    else:
        ########################################################################
        # some other item type
        ########################################################################
        item = _add_item(sh,item_path,conf=item_conf)

        
        
def _delete_item(item):
    """
    Deletes a low level item and its children from smarthome
    """
    _sh = item._sh
    path = item.id()

    # run through all children and delete them
    for child in item.return_children():
        _delete_item(child)

    # delete the item itself
    # as the items are protected in the smarthome class this hacky construction is required
    ind = _sh._SmartHome__items.index(path)
    del _sh._SmartHome__items[ind]  # path list
    del _sh._SmartHome__item_dict[path]  # key = path

    if item in _sh._SmartHome__children:
        ind = _sh._SmartHome__children.index(item) 
        del _sh._SmartHome__children[ind] # item list



def _add_item(sh,path,conf={}):
    """
    Adds a low level item to smarthome.
    Throws an exception when the item parent does not exist

    Arguments:
    smarthome: the smarthome object
    path: the item path
    conf: a dict with key value pairs of conf attributes or child items
    
    Example:
    _add_item(smarthome,'firstfloor.living.window.shading.move',{'type':'bool','knx_dpt':'1','knx_send':'2/1/5'})
    """

    # split the path to find the parent    
    parentpath = '.'.join( path.split('.')[:-1] )

    if parentpath == '':
        parent = None
    else:
        parent = sh.return_item(parentpath)
        if parent == None:
            raise Exception( 'Error: parent does not exist. {}'.format(path) )

    item = lib.item.Item(sh, parent, path, conf)
    sh.add_item(path, item)

    if parent != None:
        parent._Item__children.append(item)

    return item

