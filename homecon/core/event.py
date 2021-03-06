#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from multiprocessing import Queue

# create a queue for events
queue = Queue()


logger = logging.getLogger(__name__)


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
    reply_to : string
        ???
    """
    def __init__(self, event_type, data, source=None, target=None, reply_to=None):
        self.type = event_type
        self.data = data
        self.source = source
        self.target = target
        self.reply_to = reply_to

    @classmethod
    def fire(cls, *args, **kwargs):
        event = cls(*args, **kwargs)
        queue.put(event)

    def reply(self, data, **kwargs):
        # Event.fire(*args, target=self.reply_to, **kwargs)
        full_data = {'event': self.type, 'data': data}
        Event.fire('reply', full_data, target=self.reply_to, **kwargs)

    def __repr__(self):
        newdata = dict(self.data)
        for key in ['password', 'token']:
            if key in newdata:
                newdata[key] = '***',

        printdata = newdata.__repr__()
        if len(printdata) > 405:
            printdata = printdata[:200] + ' ... ' +printdata[-200:]

        return '<Event: {}, data: {}, source: {}, target: {}, reply_to: {}>'.format(
            self.type, printdata, self.source, self.target, self.reply_to)
