# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError
import random
import json

class cities(models.Model):
     _name = 'reserves.cities'

     name = fields.Char()
     description = fields.Text()
     coordinates = fields.Char()
     country = fields.Many2one('res.country')
     hotels = fields.One2many('reserves.hotels','city')

     @api.multi
     def current_countries(self):
         current = self.search([]).mapped('country').ids
         return {
                 'domain': {'country': [('id', 'in', current)]},
                 "type": "ir.actions.do_nothing",
                 }
 

class hotels(models.Model):
    _name = 'reserves.hotels'

    name = fields.Char()
    description = fields.Text()
    address = fields.Char()
    city = fields.Many2one('reserves.cities')
    country = fields.Many2one(related='city.country',readonly=True,store=True)
    phone = fields.Char()
    photos = fields.One2many('reserves.photos','hotel')
    #photo_small = fields.Binary()
    photo_small = fields.Binary(compute='_get_image')
    rooms = fields.One2many('reserves.rooms','hotel')
    services = fields.Many2many('reserves.services')
    comments = fields.One2many('reserves.comments','hotel')
    comments_list = fields.One2many('reserves.comments','hotel')
    stars = fields.Selection([('1','⭐'),('2','⭐ ⭐'),('3','⭐ ⭐ ⭐'),('4','⭐ ⭐ ⭐ ⭐'),('5','⭐ ⭐ ⭐ ⭐ ⭐')])
    score = fields.Selection([('1','Bad'),('2','Regular'),('3','Good'),('4','Very Good'),('5','Excelent')],compute='_get_score',readonly=True,store=True)
    past_bookings = fields.Many2many('reserves.bookings', compute = '_get_bookings')
    present_bookings = fields.Many2many('reserves.bookings', compute = '_get_bookings')
    future_bookings = fields.Many2many('reserves.bookings', compute = '_get_bookings')
# Fields per al progressbar i el sparkline:
    today_ocupation = fields.Float(compute='_get_ocupation')
    week_ocupation = fields.Char(compute='_get_ocupation')


    @api.model
    def create(self, values):
        hotel = super(hotels,self).create(values)
        for i in range(1,100):
            self.env['reserves.rooms'].create({'name':i,'hotel':hotel.id,'beds':'2','price':100.0})
        return hotel


    @api.multi
    def _get_bookings(self):
        for h in self:
            past = self.env['reserves.bookings'].search([('room.hotel.id','=',h.id)])
            h.past_bookings = past.filtered(lambda r: r.exit_day < fields.Date.today()).ids
            h.present_bookings = past.filtered(lambda r: r.exit_day > fields.Date.today() and r.checking_day <= fields.Date.today()).ids
            h.future_bookings = past.filtered(lambda r: r.checking_day > fields.Date.today()).ids 


    @api.depends('comments')
    def _get_score(self):
       for h in self:
           n = len(h.comments)
           if n>0:
            suma = sum(list(map(int,(h.comments.mapped('stars')))))
            print(str(n)+" "+str(suma))
            media = int(suma/n)
            print(media)
            if media > 0 and media <= 5:
              h.score = str(media)
            else:
               h.score='1'
           else: # No hi ha puntiacions
               h.score='1'

    @api.multi
    def _get_image(self):
       for h in self:
           print(h.photos)
           if len(h.photos)>0:
               h.photo_small = h.photos[0].photo_small

    @api.one
    def create_rooms(self):
        num=max(self.rooms.mapped('name'))+1
        self.env['reserves.rooms'].create({'name':num,'hotel':self.id,'beds':str(random.randint(1,5)),'price':random.randint(30,200)})

    @api.multi
    def create_comments(self):
       clients=self.env['reserves.bookings'].search([('checking_day','<',fields.Date.today()),('room.hotel','=',self.id)]).mapped('client').ids
       print(clients)
       if len(clients)>0: 
        print(clients)
        random.shuffle(clients)
        comment = self.env['reserves.comments'].create({'hotel':self.id,'client':clients[0],'stars':str(random.randint(1,5))})
        return {
    'name': 'Comment',
    'view_type': 'form',
    'view_mode': 'form',
    'res_model': 'reserves.comments',
    'res_id': comment.id,
    #'view_id': self.env.ref('reserves.bookings_form').id,
    'type': 'ir.actions.act_window',
    'target': 'current',
         }

    def book_it(self):
         print(self)
         print(self.env.context)
         client = self.env.context['b_client']
         room = self.env.context['b_rooms'][0][2][0] # El context ho envia en format [[6,0,[]]]
         c_day = self.env.context['b_c_day']
         e_day = self.env.context['b_e_day']
         booking = self.env['reserves.bookings'].create({'client':client,'room':room,'checking_day':c_day,'exit_day':e_day})
         return {
    'name': 'Booking',
    'view_type': 'form',
    'view_mode': 'form',
    'res_model': 'reserves.bookings',
    'res_id': booking.id,
    #'view_id': self.env.ref('reserves.bookings_form').id,
    'type': 'ir.actions.act_window',
    'target': 'current',
         }

    @api.multi
    def _get_ocupation(self):
       today = fields.Date.today()
       for h in self:
           reserves = len(self.env['reserves.bookings'].search([('room.hotel.id','=',h.id),('checking_day','<=',today),('exit_day','>',today)]))
           rooms = len(h.rooms)
           if rooms == 0:
               rooms=1
           h.today_ocupation = reserves*100.0/rooms
           #spark='[{"values":['
           values = []
           for i in range(0,7):
               nextday = fields.Date.to_string(fields.Date.from_string(today)+timedelta(days=i))
               #print(nextday)
               reserves = len(self.env['reserves.bookings'].search([('room.hotel.id','=',h.id),('checking_day','<=',nextday),('exit_day','>',nextday)]))
               #print(reserves)
           #    spark=spark+'{"label":"'+str(nextday)+'","value": "'+str(reserves)+'"}'
               values.append({'label':str(nextday),'value':str(reserves)})
           #    if i < 6:
            #       spark=spark+","
          # spark=spark+'], "area":true, "title": "Next Week", "key": "Ocupation", "color": "#7c7bad"}]'
           graph = [{'values': values, 'area': True, 'title': 'Next Week', 'key': 'Ocupation', 'color': '#7c7bad'}]
           h.week_ocupation = json.dumps(graph)
           print(graph)
    

class rooms(models.Model):
    _name = 'reserves.rooms'

    name = fields.Integer()
    comments = fields.Text()
    hotel = fields.Many2one('reserves.hotels')
    city = fields.Many2one(related='hotel.city', store=True)
    photos = fields.One2many('reserves.photosrooms','room')
    beds = fields.Selection([('1','1 Bed'),('2','2 Beds'),('3','3 Beds'),('4','1 Couple bed'),('5','1 Couple bed and 1 bed')])
    price = fields.Float()
    bookings = fields.One2many('reserves.bookings','room')

    @api.multi
    def name_get(self):
        res=[]
        for i in self:
            res.append((i.id,str(i.name)+", "+str(i.hotel.name)))
        return res

class photos(models.Model):
    _name = 'reserves.photos'

    name = fields.Char()
    hotel = fields.Many2one('reserves.hotels')
    photo = fields.Binary()
    photo_small = fields.Binary(compute='_get_images',store=True)

    @api.one
    @api.depends('photo')
    def _get_images(self):
        image = self.photo
        data = tools.image_get_resized_images(image)
        self.photo_small = data["image_medium"]
# https://www.ridingbytes.com/2016/01/04/odoo-dynamic-image-resizing/

class photosroom(models.Model):
    _name = 'reserves.photosrooms'

    name = fields.Char()
    room = fields.Many2one('reserves.rooms')
    photo = fields.Binary()
    photo_small = fields.Binary(compute='_get_images',store=True)

    @api.one
    @api.depends('photo')
    def _get_images(self):
        image = self.photo
        data = tools.image_get_resized_images(image)
        self.photo_small = data["image_medium"]


class services(models.Model):
    _name = 'reserves.services'

    name = fields.Char()
    hotels = fields.Many2many('reserves.hotels')
    description = fields.Text()
    icon = fields.Binary()
    icon_small = fields.Binary(compute='_get_images',store=True, help='ICON')

    @api.one
    @api.depends('icon')
    def _get_images(self):
        image = self.icon
        data = tools.image_get_resized_images(image)
        self.icon_small = data["image_small"]

class orderline(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    booking = fields.Many2one('reserves.bookings')
    room = fields.Many2one(related='booking.room', readonly=True) # El related es pot fer al many2one o al name
    hotel = fields.Char(related='booking.room.hotel.name',string='Hotel',readonly=True)
    client = fields.Many2one(related='booking.client',readonly=True)
    checking_day = fields.Date(related='booking.checking_day',readonly=True)
    exit_day = fields.Date(related='booking.exit_day',readonly=True)
  
    _sql_constraints = [
    ('booking_uniq', 'unique(booking)', 'There is another order line for this booking'),
    ]



class bookings(models.Model):
    _name = 'reserves.bookings'

    name = fields.Char(compute='_get_booking_name')
    city_aux = fields.Many2one('reserves.cities',store=False)
    hotel_aux = fields.Many2one('reserves.hotels',store=False)
    room = fields.Many2one('reserves.rooms',required=True)
    hotel = fields.Char(related='room.hotel.name',string='Hotel',readonly=True,store=True)
    client = fields.Many2one('res.partner',required=True)
    checking_day = fields.Date(required=True)
    exit_day = fields.Date(required=True)
    days = fields.Integer(compute='_get_days')
    color = fields.Char(compute='_get_days')
    price = fields.Float(compute='_get_price')
    order_line = fields.Many2one('sale.order.line',compute='_get_order_line',inverse='_set_order_line')
    sale_order = fields.Many2one('sale.order',related='order_line.order_id', readonly=True)

    @api.multi
    def _get_order_line(self):
        for b in self:
            b.order_line=self.env['sale.order.line'].search([('booking.id','=',b.id)]).id

    @api.one
    def _set_order_line(self):
        o = self.order_line.id
        self.env['sale.order.line'].search([('id','=',o)]).write({'booking':self.id})

    @api.one
    def create_sale(self): # Sols si no té alguna ja,
      if len(self.order_line) == 0:
        sale = self.env['sale.order'].create({'partner_id':self.client.id})
        line = self.env['sale.order.line'].create({'name':self.name,'product_id':self.env.ref('reserves.product_reserva').id,'order_id':sale.id,'price_unit':self.room.price,'booking':self.id})
        line.write({'product_uom_qty':self.days}) # Es pot fer en la creació, però per provar el write
      else:
          print('Ja té una venda')


    @api.depends('room','client','checking_day','exit_day')
    def _get_booking_name(self):
        for b in self:
            if b.room and b.client and  b.checking_day and b.exit_day: 
              b.name=(str(b.room.name)+" "+str(b.room.hotel.name)+" "+str(b.client.name)+" "+str(b.checking_day)+"/"+str(b.exit_day))


    @api.depends('checking_day','exit_day')
    def _get_days(self):
        for b in self:
            if b.checking_day and b.exit_day: 
              start=fields.Datetime.from_string(b.checking_day)
              end=fields.Datetime.from_string(b.exit_day)
              b.days=(end-start).days
              t = fields.Date.today()
              if b.checking_day > t:
                  b.color = 'future' 
              if b.checking_day < t and b.exit_day > t:
                  b.color = 'current' 
              if b.exit_day < t:
                  b.color = 'past' 
              if b.checking_day == t:
                  b.color = 'today' 

    @api.depends('days','room')
    def _get_price(self):
        for b in self:
            if b.days and b.room:
                b.price = b.room.price * b.days

    @api.constrains('checking_day','exit_day')
    def _check_date(self):
      for b in self:
        if b.days < 1:
            raise ValidationError("The dates are wrong %s %s" % (b.checking_day,b.exit_day))
        overlaped = self.search([('room.id', '=', b.room.id),('checking_day','<=',b.exit_day),('exit_day','>=',b.checking_day),('id','<>',b.id)])
        n = self.search_count([('room.id', '=', b.room.id),('checking_day','<=',b.exit_day),('exit_day','>=',b.checking_day),('id','<>',b.id)])
        if n > 0:
            raise ValidationError("The dates are overlaped %s" % overlaped.mapped('name'))

    @api.onchange('checking_day','exit_day')
    def _onchange_dates(self):
      if self.checking_day and self.exit_day:
        if self.checking_day >= self.exit_day:
            self.exit_day = fields.Datetime.to_string(fields.Datetime.from_string(self.checking_day)+timedelta(days=1))
            print(self)
            return {
               'warning': {
               'title': "Dates are Wrong",
               'message': "It's impossible to travel in time and exit before you enter in a hotel. You must leave at least 1 day after checking.",
                }
            }

    @api.onchange('city_aux')
    def _onchange_cityaux(self):
      if self.city_aux:
        self.hotel_aux=False
        self.room= False
        return {
                'domain': {'hotel_aux': [('city', '=', self.city_aux.id)]},
                }
    @api.onchange('hotel_aux')
    def _onchange_hotelaux(self):
      if self.hotel_aux:
        self.room= False
        return {
                'domain': {'room': [('hotel', '=', self.hotel_aux.id)]},
                }

class comments(models.Model):
    _name = 'reserves.comments'

    name = fields.Char(default=lambda self: fields.Datetime.now())
    comments = fields.Text()
    hotel = fields.Many2one('reserves.hotels', required=True)
    client = fields.Many2one('res.partner', required=True)
    client_photo = fields.Binary(related='client.image_small')
    stars = fields.Selection([('1','Bad'),('2','Regular'),('3','Good'),('4','Very Good'),('5','Excelent')])

    @api.constrains('client')
    def _chek_comments(self):
        for b in self:
            hotel = b.hotel.id
            client = b.client.id
            if len(self.env['reserves.bookings'].search([('room.hotel','=',hotel),('client','=',client),('checking_day','<',fields.Date.today())])) == 0:
             raise ValidationError("This client can't opine about this hotel because they have never been there %s" % b.client.name)

    @api.one
    def delete_comment(self):
        self.unlink()

class clients(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    comments = fields.One2many('reserves.comments','client')
    bookings = fields.One2many('reserves.bookings','client')
    bookings_fs = fields.Many2many('reserves.bookings',compute='_get_bfs',string="Bookings for sale")

    @api.one
    def create_sale(self):
        sale = self.env['sale.order'].create({'partner_id':self.id})
        for i in self.bookings_fs:
          line = self.env['sale.order.line'].create({'name':i.name,'product_id':self.env.ref('reserves.product_reserva').id,'order_id':sale.id,'price_unit':i.room.price,'booking':i.id})
          line.write({'product_uom_qty':i.days}) # Es pot fer en la creació, però per provar el write

    @api.multi
    def _get_bfs(self):
        for c in self:
            c.bookings_fs = c.bookings.filtered(lambda r: len(r.order_line) == 0).ids


class w_clients_bookings(models.TransientModel):
     _name = 'reserves.w_clients_bookings'

     def _default_client(self):
         print(str(self._context.get('active_id'))+'*******************************')
         return self.env['res.partner'].browse(self._context.get('active_id')) # Aquest mètode permet agafar el active_id del context. 

     def _default_bookings(self):
         print(str(self._context.get('b_fs'))+'*******************************')
         #return self.env['reserves.bookings'].browse(self._context.get('b_fs'))
         return self._context.get('b_fs')

     client = fields.Many2one('res.partner',default=_default_client)
     bookings = fields.Many2many('reserves.bookings', relation='b_w',default=_default_bookings) # Els que selecciona el client
     bookings_fs = fields.Many2many('reserves.bookings',relation='b_fs_w', readonly=True, default=_default_bookings) # Tots els possibles, per a facilitat el domain en el wizard

     @api.one
     def accept(self):
       print('Acceptat')
       print(self.bookings)
       sale = self.env['sale.order'].create({'partner_id':self.client.id})
       for i in self.bookings:
          line = self.env['sale.order.line'].create({'name':i.name,'product_id':self.env.ref('reserves.product_reserva').id,'order_id':sale.id,'price_unit':i.room.price,'booking':i.id})
          line.write({'product_uom_qty':i.days}) # Es pot fer en la creació, però per provar el write

       return {}


class w_bookings(models.TransientModel):
     _name = 'reserves.w_bookings'

     state = fields.Selection([
        ('client', "Client and Country"),
        ('city', "City Selection"),                                                                        
        ('requirements', "Requirements"),                                                                        
        ('room', "Room Selection"),                                                                        
      ], default='client')

     client = fields.Many2one('res.partner', required=True)
     countries = fields.Many2many('res.country',default=lambda r: r.env['reserves.cities'].search([]).mapped('country').ids)
     country = fields.Many2one('res.country') # en la vista es filtren els que no tenen ciutats
     city = fields.Many2one('reserves.cities')
     stars = fields.Selection([('0','any'),('1','⭐'),('2','⭐ ⭐'),('3','⭐ ⭐ ⭐'),('4','⭐ ⭐ ⭐ ⭐'),('5','⭐ ⭐ ⭐ ⭐ ⭐')], default='0' )
     score = fields.Selection([('1','Bad'),('2','Regular'),('3','Good'),('4','Very Good'),('5','Excelent')],string='Minimum Score')
     hotels = fields.Many2many('reserves.hotels',readonly=True, string='Hotels Available')
     rooms = fields.Many2many('reserves.rooms',string='Rooms Available')
     hotel = fields.Many2one('reserves.hotels',string='Select Hotel')
     services = fields.Many2many('reserves.services')
     beds = fields.Selection([('0','any'),('1','1 Bed'),('2','2 Beds'),('3','3 Beds'),('4','1 Couple bed'),('5','1 Couple bed and 1 bed')], default='0')
     checking_day = fields.Date(required=True)
     exit_day = fields.Date(required=True)

     def apply_filters(self):
         domains = []
         if len(self.city) != 0:
             domains.append(('city.id','=',str(self.city.id)))
             if self.score:
                 domains.append(('score','>=',self.score))
             if self.stars != '0':
                 domains.append(('stars','=',self.stars))
         print(domains)
         h = self.env['reserves.hotels'].search(domains)
         print("Hotels:::::::::::"+str(h.mapped('name')))
         if len(self.services) > 0:
             s = self.services
             h = h.filtered(lambda r: len(r.services & s) == len(s) ) # & interesecció de recordsets
    # Trobar els hotels i habitacions disponibles:
         if len(self.city) != 0: 
             self.hotels = h.sorted(key=lambda r: r.score, reverse=True).ids ## Els hotels
             if self.checking_day and self.exit_day:
                rooms = self.env['reserves.rooms'].search([('hotel.id','in',h.ids)]) ## La llista de rooms dels hotels
                # Cal trobar la llista de reserves que es solapen amb les dates seleccionades
                overlaped = self.env['reserves.bookings'].search([('checking_day','<=',self.exit_day),('exit_day','>=',self.checking_day)]).mapped('room')
                free = rooms - overlaped # Totes les habitacions dels hotels menys totes les habitacions
                 # de totes les reserves
                if self.beds != '0':
                  free.filtered(lambda r: r.beds == self.beds)
                self.hotels = free.mapped('hotel').sorted(key=lambda r: r.score, reverse=True).ids
                self.rooms = free.ids


     def accept(self):
       print('acceptat')
       room = self.rooms.filtered(lambda r: r.hotel.id == self.hotel.id)[0]
       print(room)
       booking = self.env['reserves.bookings'].create({'client':self.client.id,'room':room.id,'checking_day':self.checking_day,'exit_day':self.exit_day})
       print(booking)
       return {
    'name': 'Booking',
    'view_type': 'form',
    'view_mode': 'form',
    'res_model': 'reserves.bookings',
    'res_id': booking.id,
    #'view_id': self.env.ref('reserves.bookings_form').id,
    'type': 'ir.actions.act_window',
    'target': 'current',
      }



     @api.onchange('country')
     def change_country(self):
         if len(self.country) > 0: 
          self.state='city'
          return {'domain': {'city': [('country','=',self.country.id)]}}

     @api.onchange('city','services','stars','beds','score')
     def change_city(self):
        if len(self.city) > 0: 
          self.state='requirements'
        self.apply_filters()
          #return {'domain': {'hotels': [('city','=',self.city.id)]}}
        return {}


     @api.onchange('checking_day','exit_day')
     def _onchange_dates(self):
      if self.checking_day and self.exit_day:
        if self.checking_day >= self.exit_day:
            self.exit_day = fields.Datetime.to_string(fields.Datetime.from_string(self.checking_day)+timedelta(days=1))
            print(self)
            return {
               'warning': {
               'title': "Dates are Wrong",
               'message': "It's impossible to travel in time and exit before you enter in a hotel. You must leave at least 1 day after checking.",
                }
            }
        else:
            self.state='room'
            #h = self.env['reserves.hotels'].search([('city','=',self.city.id)])
            #print(h)
            #if self.stars != '0':
             #   h = h.filtered(lambda r: r.stars == self.stars)
            #for s in self.services:
             #   print(s)
            #print(h)
            self.apply_filters()
        return {}
 


