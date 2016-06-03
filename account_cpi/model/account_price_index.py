# -*- coding: utf-8 -*-

from openerp import fields, models


class PriceIndex(models.Model):
    _name = 'account.price.index'

    period_id = fields.Many2one(
        'account.period',
        ondelete='cascade',
        string="Period",
        required=True,
    )
    index_value = fields.Float(
        string="Price Index"
    )
    _sql_constraints = [
        ('period_unique',
         'UNIQUE(period_id)',
         "Only One Price Index per Fiscal Period"),
    ]
