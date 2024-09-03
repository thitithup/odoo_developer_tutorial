# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from email.policy import default

from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"

    name = fields.Char(required=True)
    color = fields.Integer(string="Color Index")

    _order = 'name'

    _sql_constraints = [
        ('name_unique', 'unique (name)', "Name of tag must be unique."),
    ]
