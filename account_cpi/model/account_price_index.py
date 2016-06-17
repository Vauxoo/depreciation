# -*- coding: utf-8 -*-

from openerp import fields, models


class PriceIndex(models.Model):
    _name = 'account.price.index'

    period_id = fields.Many2one(
        'account.period',
        ondelete = 'cascade',
        string = "Period",
        help = "Relation to a Valid Stored Period. Unique.",
        required = True,

    )
    start_date = fields.Date(
        string = "Start Date of Period",
        store = True,
        readonly = True,
        related = "period_id.date_start"
    )
    end_date = fields.Date(
        string = "End Date of Period",
        store = True,
        readonly = True,
        related = "period_id.date_stop"
    )
    index_value = fields.Float(
        string = "Price Index",
        help = "Consumer Price Index for a Specific Fiscal Period.",
    )
    _sql_constraints = [
        ('period_unique',
         'UNIQUE(period_id)',
         "Only One Price Index per Fiscal Period"),
    ]
