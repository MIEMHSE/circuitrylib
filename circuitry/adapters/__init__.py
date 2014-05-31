#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'


class AbstractAdapter(object):
    default_method = None
    default_content_type = 'text/plain'
    public_methods = None
    public_properties = None
    _device = None
    _options = None

    def __init__(self, device, **kwargs):
        if self._options is None:
            self._options = dict()
        self._options.update(kwargs)
        self._device = device