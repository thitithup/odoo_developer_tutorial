# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from email.policy import default

from odoo import fields, models, api, Command
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=1)

    def button_sold(self):
        res = super(EstateProperty, self).button_sold()
        # customer_journal_id = 1 ## หาใน Master: Journal <Accounting>
        # Finding Customer Inoice Journal first record found
        customer_journal_id = self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id
        # account.move.line (Account move line)
        invoice = self.env["account.move"].create(
            {
                'partner_id': self.buyer_id.id,
                'journal_id': customer_journal_id,
                'move_type': 'out_invoice',
                "invoice_line_ids": [
                    Command.create({
                        "name": self.name,
                        "quantity": 1,
                        "price_unit": round(self.selling_price * 0.06, 2),
                    }),
                    Command.create({
                        "name": 'Fee',
                        "quantity": 1,
                        "price_unit": 100,
                    })
                ],
            }
        )
        self.write({'invoice_id': invoice.id})
        return res

