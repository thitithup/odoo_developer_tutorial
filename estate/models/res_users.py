# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'Inherit res.users for estate.property'

    property_ids = fields.One2many('estate.property', 'salesman_id', string="Properties")
    property2_ids = fields.One2many('estate.property', 'salesman_id', string="Properties",
                                    compute='_get_property')

    def _get_property(self):
        for record in self:
            record.property2_ids = self.env['estate.property'].search([('salesman_id', '=', record.id),
                                                                       ('state','not in', ['sold','canceled'])])

