# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from email.policy import default

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(string="Available From",
                                    # default=fields.Date.today,
                                    copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=1, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ])
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled'),
    ], string="Status", default='new', required=True)
    active = fields.Boolean(default=False)

    property_type_id = fields.Many2one('estate.property.type',
                                       string="Property Type")
    salesman_id = fields.Many2one('res.users',
                                  string="Salesman")
    buyer_id = fields.Many2one('res.partner', string="Buyer")

    tag_ids = fields.Many2many('estate.property.tag', string="Property Tags")

    offer_ids = fields.One2many('estate.property.offer', 'property_id',
                                string="Offers")

    # total_area = fields.Integer(compute='_compute_total_area', string="Total Area (sqm)")
    total_area = fields.Integer(string="Total Area (sqm)")

    # best_offer = fields.Float(string='Best Offer', compute='_compute_best_offer')
    best_offer = fields.Float(string='Best Offer', copy=False)

    _sql_constraints = [
        ('name_unique', 'unique (name)', "Title of Property must be unique."),
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be positive'),
        ('selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive'),
    ]

    _order = 'id desc'

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            # if record.selling_price and record.selling_price <= 0:
            #     raise ValidationError("The selling price must be positive")
            if record.selling_price:
                if record.selling_price < record.expected_price * 0.9:
                    raise ValidationError("The selling price cannot be lower than 90% of the expected price")

    @api.onchange('offer_ids')
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = 0
            if record.offer_ids:
                filter_ids = record.offer_ids.filtered(lambda l: l.date_deadline >= fields.Date.today())
                record.best_offer = max(filter_ids.mapped('price'))

    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
        # self.total_area = self.living_area + self.garden_area

    @api.onchange('living_area', 'garden_area')
    def _onchange_area(self):
        self.total_area = self.living_area + self.garden_area

    @api.onchange('garden')
    def _onchange_gardent(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 10
        else:
            self.garden_orientation = False
            self.garden_area = 0

    def button_sold(self):
        if self.state == 'canceled':
            raise UserError("You cannot sell a canceled property")
        self.state = 'sold'
        # self.active = False

    def button_cancel(self):
        self.state = 'canceled'
        # self.active = False

    def button_draft(self):
        self.state = 'new'
        # self.active = True

    def unlink(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError("You cannot delete a property that is not new or canceled")
        return super(EstateProperty, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = "{} (Copy)".format(self.name)
        return super(EstateProperty, self).copy(default=default)

    # def write(self, vals):
    #     res = super(EstateProperty, self).write(vals)
    #     if self.offer_ids:
    #         self.state = 'offer_received'
    #     else:
    #         self.state = 'new'
    #     # print(len(self.offer_ids))
    #     return res