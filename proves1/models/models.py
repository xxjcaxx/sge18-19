# -*- coding: utf-8 -*-

from odoo import models, fields, api
import random

class proves1(models.Model):
     _name = 'proves1.proves1'

     name = fields.Char()
     value = fields.Integer()
     value2 = fields.Float(compute="_value_pc", store=False)
     pais = fields.Many2one('res.country')
#     description = fields.Text()
#
     @api.depends('value')
     def _value_pc(self):
         self.value2 = float(self.value) / 100

class course(models.Model):
    _name = 'proves1.course'
    name = fields.Char()
    students = fields.One2many('proves1.student','course')
    teachers = fields.Many2many('proves1.teacher')
    tutor = fields.Many2many(comodel_name='proves1.teacher',
                            relation='courses_tutors',
                            column1='course',
                            column2='tutor')

class student(models.Model):
    _name = 'proves1.student'
    name = fields.Char()
    course = fields.Many2one('proves1.course')
    subjects = fields.One2many('proves1.eval','student')
    country = fields.Many2one('res.country')
    currency = fields.Char(related='country.currency_id.symbol',store=False,readonly=True)
    aleatori = fields.Char(compute='_compute_aleatori')
    a = fields.Integer()
    b = fields.Integer()
    ab = fields.Integer(compute='_get_ab')

    @api.multi
    def _compute_aleatori(self):
      for record in self:
        record.aleatori = str(random.randint(1, 1e6))+str(record.country.currency_id.symbol)

    @api.depends('a','b')
    def _get_ab(self):
        for r in self:
            r.ab = r.a+r.b

class teacher(models.Model):
    _name = 'proves1.teacher'
    name = fields.Char()
    courses = fields.Many2many('proves1.course')
    tutor = fields.Many2many(comodel_name='proves1.course',
                            relation='courses_tutors',
                            column1='tutor',
                            column2='course')

class subject(models.Model):
    _name = 'proves1.subject'
    name = fields.Char()
    students = fields.One2many('proves1.eval','subject')

class evaluation(models.Model):
    _name = 'proves1.eval'
    name = fields.Char()
    evaluation = fields.Float()
    student = fields.Many2one('proves1.student')
    subject = fields.Many2one('proves1.subject')


