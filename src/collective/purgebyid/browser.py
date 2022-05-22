# -*- coding: utf-8 -*-
from collective.purgebyid.api import mark_involved_objects
from Products.Five.browser import BrowserView


class MarkInvolvedView(BrowserView):
    """Useful utility view to mark IDs in page templates.

    In offers two ways for using it:

    1. marking objects (with UUID)

        tal:define="purgebyid nocall:context/@@purgebyid"
        ...
        <tal:mark-involved tal:define="python:purgebyid.mark(image1)" />
        <tal:mark-involved tal:define="python:purgebyid.mark(image2)" />
        <tal:mark-involved tal:define="python:purgebyid.mark(image3, image4)" />
        <tal:mark-involved tal:define="python:purgebyid.mark(*images)" />

    2. marking arbitrary IDs

        tal:define="purgebyid nocall:image/@@purgebyid"
        ...
        <tal:mark-involved tal:define="python:purgebyid.mark('0b05ba53734965c6e48bdcd2c7c7e41f')" />
    """

    def mark(self, *args):
        """Mark an ID as being involved for delivering the current request"""
        mark_involved_objects(self.request, args)
