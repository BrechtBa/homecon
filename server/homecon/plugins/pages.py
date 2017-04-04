#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import uuid

from .. import core
from .authentication import jwt_decode

class Pages(core.plugin.Plugin):
    """
    Notes
    -----
    A homecon app is structured using groups, pages, sections and widgets

    """

    def initialize(self):

        self._db_groups = core.database.Table(core.db,'pages_groups',[
            {'name':'path',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'config',      'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'order',       'type':'int(8)',     'null': '',  'default':'',  'unique':''},
        ])
        self._db_pages = core.database.Table(core.db,'pages_pages',[
            {'name':'path',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'group',       'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'config',      'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'order',       'type':'int(8)',     'null': '',  'default':'',  'unique':''},
        ])
        self._db_sections = core.database.Table(core.db,'pages_sections',[
            {'name':'path',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'page',        'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'config',       'type':'char(255)', 'null': '',  'default':'',  'unique':''},
            {'name':'order',       'type':'int(8)',     'null': '',  'default':'',  'unique':''},
        ])
        self._db_widgets = core.database.Table(core.db,'pages_widgets',[
            {'name':'path',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'section',     'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'type',        'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'config',      'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'order',       'type':'int(8)',     'null': '',  'default':'',  'unique':''},
        ])

        # local references
        self._groups = {}
        self._pages = {}
        self._sections = {}
        self._widgets = {}


        # load data from the database
        result = self._db_groups.GET()
        for group in result:
            self.add_group_local(group['path'],json.loads(group['config']),group['order'])

        result = self._db_pages.GET()
        for page in result:
            self.add_page_local(page['path'],page['group'],json.loads(page['config']),page['order'])

        result = self._db_sections.GET()
        for section in result:
            self.add_section_local(section['path'],section['page'],json.loads(section['config']),section['order'])

        result = self._db_widgets.GET()
        for widget in result:
            self.add_widget_local(widget['path'],widget['section'],widget['type'],json.loads(widget['config']),widget['order'])


        # define defaults
        if len(self._groups) == 0:
            self.add_group({'title':'Home'})
            self.add_group({'title':'Central'})
            self.add_group({'title':'Ground floor'})

        if len(self._pages) == 0:
            self.add_page('home',{'title':'Home','icon':'blank'})
            self.add_page('central',{'title':'Heating','icon':'sani_heating'})
            self.add_page('groundfloor',{'title':'Living room','icon':'scene_livingroom'})
            self.add_page('groundfloor',{'title':'Kitchen','icon':'scene_dinner'})

        if len(self._sections) == 0:
            s = self.add_section('home/home',{'type':'transparent'})

            self.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':0},order=None)
            self.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':24},order=None)
            self.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':48},order=None)
            self.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':72},order=None)


        logging.debug('Pages plugin Initialized')

    def add_group_local(self,path,config,order):
        """
        """
        
        group = {'path':path,'config':config,'order':order}
        self._groups[path] = group
        
        return group


    def add_group(self,config,order=None):
        """
        """

        if 'title' in config:
            temppath = self._title_to_path(config['title'])
            path = temppath
            i = 1
            while path in self._groups:
                i += 1
                path = '{}{}'.format(temppath,i)
        else:
            path = str(uuid.uuid4())

        if order is None:
            order = self._get_next_order(self._groups)

        self._db_groups.POST(path=path,config=json.dumps(config),order=order)
        group = self.add_group_local(path,config,order)

        return group

    def update_group(self,path,config):
        """
        """

        group =  self._groups[path]
        for key in config:
            group['config'][key] = config[key]

        self._db_groups.PUT(config=json.dumps(group['config']),where='path=\'{}\''.format(path))

        return group

    def delete_group(self,path):
        """
        """
    
        del self._groups[path]
        self._db_groups.DELETE(path=path)

        # cascade
        for page in self._pages.values():
            if page['group'] == path:
                self.delete_page(page['path'])

    def add_page_local(self,path,group,config,order):
        """
        """
        
        page = {'path':path,'group':group,'config':config,'order':order}
        self._pages[path] = page
        
        return page


    def add_page(self,group,config,order=None):
        """
        """

        basepath = self._groups[group]['path'] + '/'
        if 'title' in config:
            temppath = basepath + self._title_to_path(config['title'])
            path = temppath
            i = 1
            while path in self._pages:
                i += 1
                path = '{}{}'.format(temppath,i)
        else:
            path = basepath + str(uuid.uuid4())

        if order is None:
            order = self._get_next_order(self._pages)

        self._db_pages.POST(path=path,group=group,config=json.dumps(config),order=order)
        page = self.add_page_local(path,group,config,order)
        
        return page

    def update_page(self,path,config):
        """
        """

        page =  self._pages[path]
        for key in config:
            page['config'][key] = config[key]

        self._db_pages.PUT(config=json.dumps(page['config']),where='path=\'{}\''.format(path))

        return page

    def delete_page(self,path):
        """
        """
    
        del self._pages[path]
        self._db_pages.DELETE(path=path)

        # cascade
        for section in self._sections.values():
            if section['page'] == path:
                self.delete_section(section['path'])


    def add_section_local(self,path,page,config,order):
        """
        """
        
        section = {'path':path,'page':page,'config':config,'order':order}
        self._sections[path] = section
        
        return section

    def add_section(self,page,config=None,order=None):
        """
        """
        
        path = str(uuid.uuid4())
        
        if config is None:
            config = {}

        if order is None:
            order = self._get_next_order(self._sections)

        self._db_sections.POST(path=path,page=page,config=json.dumps(config),order=order)
        section = self.add_section_local(path,page,config,order)
        
        return section

    def update_section(self,path,config):
        """
        """

        section =  self._sections[path]
        for key in config:
            section['config'][key] = config[key]

        self._db_sections.PUT(config=json.dumps(section['config']),where='path=\'{}\''.format(path))

        return section

    def delete_section(self,path):
        """
        """
    
        del self._sections[path]
        self._db_sections.DELETE(path=path)

        # cascade
        for widget in self._widgets.values():
            if widget['section'] == path:
                self.delete_widget(widget['path'])


    def add_widget_local(self,path,section,widgettype,config,order):
        """
        """
        
        widget = {'path':path,'section':section,'type':widgettype,'config':config,'order':order}
        self._widgets[path] = widget
        
        return section

    def add_widget(self,section,widgettype,config=None,order=None):
        """
        """
        
        path = str(uuid.uuid4())
        
        if config is None:
            config = {}

        if order is None:
            order = self._get_next_order(self._widgets)


        self._db_widgets.POST(path=path,section=section,type=widgettype,config=json.dumps(config),order=order)
        widget = self.add_widget_local(path,section,widgettype,config,order)
        
        return widget

    def update_widget(self,path,config):
        """
        """

        widget =  self._widgets[path]
        for key in config:
            widget['config'][key] = config[key]

        self._db_widgets.PUT(config=json.dumps(widget['config']),where='path=\'{}\''.format(path))

        return widget

    def delete_widget(self,path):
        """
        """
    
        del self._widgets[path]
        self._db_widgets.DELETE(path=path)



    def get_menu(self):
        """
        """

        groups = []
        for key,group in self._groups.items():
            if not key == 'home':
                pages = []
                for key,page in self._pages.items():
                    if page['group'] == group['path']:
                        pages.append({'path':page['path'],'config':page['config']})

                pages = sorted(pages, key=lambda x:self._pages[x['path']]['order'])

                group = {
                    'path': group['path'],
                    'config': group['config'],
                    'pages' : pages
                }

                groups.append(group)
                groups = sorted(groups, key=lambda x:self._groups[x['path']]['order'])

        return groups

    def get_pages_paths(self):
        pages = [page['path'] for page in self._pages.values()]
        pages = sorted(pages,key=lambda x:self._pages[x]['order'])
        return pages

    def get_page(self,path):
        """
        """

        sections = [section['path'] for section in self._sections.values() if section['page'] == path]
        sections = sorted(sections, key=lambda x:self._sections[x]['order'])

        page = {
            'path': self._pages[path]['path'],
            'config': self._pages[path]['config'],
            'sections': sections,
        }

        return page

    def set_page(self,path,config):
        """
        """

        page = self._pages[path]
        page['config'] = config
        self._db_pages.PUT(config=json.dumps(page['config']), where='path=\'{}\''.format(page['path']))

        return page

    def get_section(self,path):
        """
        """

        widgets = [widget['path'] for widget in self._widgets.values() if widget['section'] == path]
        widgets = sorted(widgets, key=lambda x:self._widgets[x]['order'])

        section = {
            'path': self._sections[path]['path'],
            'config': self._sections[path]['config'],
            'widgets': widgets,
        }

        return section


    def get_widget(self,path):
        """
        """

        return self._widgets[path]



    def listen_pages_menu(self,event):
        
        tokenpayload = jwt_decode(event.data['token'])
        
        if tokenpayload and tokenpayload['permission'] > 1:
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])

    def listen_pages_paths(self,event):
        
        tokenpayload = jwt_decode(event.data['token'])
        
        if tokenpayload and tokenpayload['permission'] > 1:
            core.websocket.send({'event':'pages_paths', 'path':'', 'value':self.get_pages_paths()}, clients=[event.client])

    def listen_pages_group(self,event):

        tokenpayload = jwt_decode(event.data['token'])

        if 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # delete
            self.delete_group(event.data['path'])
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # update
            self.update_group(event.data['path'],event.data['value'])
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])

        if not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
            # add
            self.add_group({'title':'newgroup'})
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])

    def listen_pages_page(self,event):

        tokenpayload = jwt_decode(event.data['token'])

        if 'path' in event.data and not 'value' in event.data and tokenpayload and tokenpayload['permission'] > 1:
            # get
            if event.data['path'] in self._pages:
                page = self.get_page(event.data['path'])
                core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])

            else:
                logging.warning('{} not in pages'.format(event.data['path']))

        elif 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # delete
            self.delete_page(event.data['path'])
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
            core.websocket.send({'event':'pages_paths', 'path':'', 'value':self.get_pages_paths()}, clients=[event.client])
            
        elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # update
            page = self._pages[event.data['path']]
            self.update_page(event.data['path'],event.data['value']['config'])
            page = self.get_page(event.data['path'])
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
            core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])


        elif not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
            # add
            self.add_page(event.data['group'],{'title':'newpage','icon':'blank'})
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
            core.websocket.send({'event':'pages_paths', 'path':'', 'value':self.get_pages_paths()}, clients=[event.client])


    def listen_pages_section(self,event):

        tokenpayload = jwt_decode(event.data['token'])

        if 'path' in event.data and not 'value' in event.data and tokenpayload and tokenpayload['permission'] > 1:
            # get
            section = self.get_section(event.data['path'])
            core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # delete
            pagepath = self._sections[event.data['path']]['page']
            self.delete_section(event.data['path'])
            page = self.get_page(pagepath)
            core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # update
            self.update_section(event.data['path'],event.data['value']['config'])
            section = self.get_section(event.data['path'])
            core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])

        elif not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
            # add
            self.add_section(event.data['page'],{'title':'newsection','type':'raised'})
            page = self.get_page(event.data['page'])
            core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])


    def listen_pages_widget(self,event):

        tokenpayload = jwt_decode(event.data['token'])

        if 'path' in event.data and not 'value' in event.data and tokenpayload and tokenpayload['permission'] > 1:
            # get
            widget = self.get_widget(event.data['path'])
            core.websocket.send({'event':'pages_widget', 'path':widget['path'], 'value':widget}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # delete
            sectionpath = self._widgets[event.data['path']]['section']
            self.delete_widget(event.data['path'])
            section = self.get_section(sectionpath)
            core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # update
            self.update_widget(event.data['path'],event.data['value']['config'])
            widget = self._widgets[event.data['path']]
            core.websocket.send({'event':'pages_widget', 'path':widget['path'], 'value':widget}, clients=[event.client])

        elif not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
            # add
            self.add_widget(event.data['section'],event.data['type'],{'initialize':True})
            section = self.get_section(event.data['section'])
            core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])










    def _get_next_order(self,data):
        """
        Parameters
        ----------
        data : dict
            a dictionary with an order key
        """
        order = 0
        for d in data.values():
            order = max(order,d['order'])

        order += 1

        return order


    def _title_to_path(self,title):
        return title.lower().replace(' ','')

