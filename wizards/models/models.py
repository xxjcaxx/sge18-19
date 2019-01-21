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



class w_reserves(models.TransientModel):
     _name = 'wizards.w_reserves'
 
     def _default_teatre(self):
         return self.env['wizards.teatres'].browse(self._context.get('active_id')) # El context conté, entre altre coses, el active_id del model que està obert.
 
     teatre = fields.Many2one('wizards.teatres',default=_default_teatre)
     obra = fields.Many2one('wizards.obres')
     actuacio = fields.Many2one('wizards.actuacions',required=True)
     butaca = fields.Many2one('wizards.butaques',required=True)
     state = fields.Selection([
        ('teatre', "Teatre Selection"),
        ('obra', "Obra Selection"),                                             
        ('actuacio', "Actuacio Selection"),
        ('butaca', "butaca Selection"),
        ('fin', "Fin"),
        ], default='teatre')
 
 
     @api.onchange('teatre')
     def _oc_teatre(self):
        if len(self.teatre) > 0:
         actuacions = self.env['wizards.actuacions'].search([('teatre','=',self.teatre.id)])
         print(actuacions)
         obres = actuacions.mapped('obra')
         print(obres)
         self.state='obra'
         return { 'domain': {'obra': [('id', 'in', obres.ids)]},}

     @api.onchange('obra')
     def _oc_obra(self):
        if len(self.obra) > 0:
          actuacions = self.env['wizards.actuacions'].search([('teatre','=',self.teatre.id),('obra','=',self.obra.id)])

          self.state='actuacio'
          return { 'domain': {'actuacio': [('id', 'in', actuacions.ids)]},}


     @api.onchange('actuacio')
     def _oc_actuacio(self):
        if len(self.actuacio) > 0:
          print('butaques ******************************************')
          butaques = self.env['wizards.butaques'].search([('teatre','=',self.actuacio.teatre.id)])
          b_reservades = self.actuacio.reserves.mapped('butaca')
          print(b_reservades)
          b_disponibles = butaques - b_reservades
          print(b_disponibles)

          self.state='butaca'
          return { 'domain': {'butaca': [('id', 'in', b_disponibles.ids)]},}

     @api.onchange('butaca')
     def _oc_butaca(self):
        if len(self.butaca) > 0:
            self.state='fin'

     @api.multi
     def reserva(self):
         reserva = self.env['wizards.reserves'].create({'actuacio':self.actuacio.id,'butaca':self.butaca.id,'name':str(self.actuacio.name)+" - "+str(self.butaca.name)})
         return {
    'name': 'Reserves',
    'view_type': 'form',
    'view_mode': 'form',
    'res_model': 'wizards.reserves',
    'res_id': reserva.id,
    'context': self._context,
    'type': 'ir.actions.act_window',
    'target': 'current',
                 }

