# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class teatres(models.Model):
     _name = 'wizards.teatres'

     name = fields.Char()
     actuacions = fields.One2many('wizards.actuacions','teatre')
     butaques = fields.One2many('wizards.butaques','teatre')

     @api.multi
     def generar_butaques(self):
         for t in self:
             for i in range(1,100):
                 self.env['wizards.butaques'].create({'name':i,'teatre':t.id})

class obres(models.Model):
     _name = 'wizards.obres'

     name = fields.Char()
     actuacions = fields.One2many('wizards.actuacions','obra')
     @api.multi
     def generar_actuacions(self):
         for o in self:
             for t in self.env['wizards.teatres'].search([]):
                 for i in range(1,10):
                     data = fields.Datetime.to_string(fields.Datetime.from_string(fields.Datetime.now())+timedelta(days=1))
                     self.env['wizards.actuacions'].create({'name':str(o.name)+str(t.name)+str(i),'teatre':t.id,'obra':o.id,'data':data})

class actuacions(models.Model):
     _name = 'wizards.actuacions'

     name = fields.Char()
     teatre = fields.Many2one('wizards.teatres')
     obra = fields.Many2one('wizards.obres')
     data = fields.Datetime()
     reserves = fields.One2many('wizards.reserves','actuacio')

class reserves(models.Model):
     _name = 'wizards.reserves'

     name = fields.Char()
     actuacio = fields.Many2one('wizards.actuacions')
     butaca = fields.Many2one('wizards.butaques')


class butaques(models.Model):
     _name = 'wizards.butaques'

     name = fields.Integer()
     teatre = fields.Many2one('wizards.teatres')




