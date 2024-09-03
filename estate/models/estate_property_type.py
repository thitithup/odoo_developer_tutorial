# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from email.policy import default

from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id',
                                   string="Properties")
    offer_count = fields.Integer(
        string='Number of Offers',
        store=False, readonly=True, compute='_count_offer')

    sequence = fields.Integer(string='Sequence', default=10)

    # _order = 'name'

    _sql_constraints = [
        ('name_unique', 'unique (name)', "Name of type must be unique."),
    ]

    def _count_offer(self):
        for record in self:
            record.offer_count = len(record.property_ids.mapped('offer_ids'))

    def button_dummy(self):
        print("Button clicked")