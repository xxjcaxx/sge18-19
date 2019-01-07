# -*- coding: utf-8 -*-

from odoo import models, fields, api

class (models.Model):
     _name = 'vistes.vistes'

     name = fields.Char()
     value = fields.Integer()

