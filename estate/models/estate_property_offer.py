# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from email.policy import default

from odoo import fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

from odoo.addons.crm.models.res_users import Users


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float(string="Price", required=True)
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused')],
        string="Status", copy=False)
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    property_id = fields.Many2one('estate.property', string="Property", required=True)

    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline")

    # _order = 'price desc'

    _sql_constraints = [
        ('price', 'CHECK(price > 0)', 'The price must be positive'),
    ]

    @api.onchange("validity")
    def _onchange_validity(self):
        for record in self:
            record.date_deadline = datetime.now() + timedelta(days=record.validity)

    @api.onchange('date_deadline')
    def _onchange_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - datetime.now().date()).days

    def button_accept(self):
        if not self.property_id.selling_price:
            self.property_id.selling_price = self.price
            self.property_id.buyer_id = self.partner_id.id
            # for offer in self.property_id.offer_ids:
            #     if offer.id != self.id:
            #         offer.status = 'refused'
            self.property_id.offer_ids.filtered(lambda offer: offer.id != self.id).button_refuse()
        else:
            raise UserError("This property already has a selling price.")
        self.status = 'accepted'

    def button_refuse(self):
        self.status = 'refused'
        # for record in self:
        #     record.status = 'refused'

    def button_draft(self):
        if self.status == 'accepted':
            self.property_id.selling_price = 0
            self.property_id.buyer_id = False
        self.status = False

    @api.model_create_multi
    def create(self, vals_list):
        if 'price' in vals_list[0]:
            if vals_list[0]['price'] <= 0:
                raise UserError("The price must be positive")
        price = vals_list[0]['price']
        history = self.env['estate.property.offer'].search([('property_id', '=', vals_list[0]['property_id'])],
                                                             order='price desc', limit=1)
        if history and history.price > price:
            raise UserError("The price must be higher than the last offer")

        res = super(EstatePropertyOffer, self).create(vals_list)
        property = self.env['estate.property'].browse(vals_list[0]['property_id'])
        property.write({'state': 'offer_received'})
        return res

    def unlink(self):
        property = self.property_id
        res = super(EstatePropertyOffer, self).unlink()
        if not property.offer_ids:
            property.write({'state': 'new'})
        return res