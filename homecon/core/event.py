#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Queue

# create a queue for events
queue = Queue()


class Event(object):
    """

    Parameters
    ----------
    event_type : string
        The event type.
    data : dict
        The data describing the event.
    source : string
        The source of the event.
    target : string
        The target of the event.
    client : string
        ???
    """
    def __init__(self, event_type, data, source, target=None, client=None):
        self.type = event_type
        self.data = data
        self.source = source
        self.target = target
        self.client = client

    @classmethod
    def fire(cls, *args, **kwargs):
        event = cls(*args, **kwargs)
        queue.put(event)

    def __repr__(self):
        newdata = dict(self.data)
        for key in ['password', 'token']:
            if key in newdata:
                newdata[key] = '***'

        printdata = newdata.__repr__()
        if len(printdata) > 405:
            printdata = printdata[:200] + ' ... ' +printdata[-200:]

        return '<Event: {}, data: {}, source: {}, client: {}>'.format(
            self.type, printdata, self.source, self.client)
