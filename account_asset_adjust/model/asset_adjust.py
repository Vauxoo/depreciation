# -*- coding: utf-8 -*-
# import time
from datetime import datetime
# from dateutil.relativedelta import relativedelta

from openerp import api, fields, models


class AdjustableAsset(models.Model):
    _inherit = 'account.asset.asset'

    adjusted_initial_values_ids = fields.One2many(
        'account.asset.adjust.initial',
        'asset_id', string="Initial Adjustment"
    )

    @api.depends('purchase_date')
    def _adjust_initial_values(self):
#        for r in self:
        self.ensure_one()
        purchase_period = datetime.strptime(
            self.purchase_date, '%Y-%m-%d'
        ).replace(day=1)
        cpi_list = self.env["account.cpi"].search(
            [
               ("start_date", ">=", purchase_period),
            ],
            order="start_date asc",
        )
        first_idx = cpi_list[0].index_value
        for cpi in cpi_list:
            adj_factor = cpi.index_value/first_idx
            self.env['account.asset.adjust.initial'].create({
                asset_id: self.id,
                period_id: cpi.period_id,
                adjust_factor: adj_factor,
            })

class InitialAdjustmentLine(models.Model):
    _name = 'account.asset.adjust.initial'
    _description = "Initial Adjustment for Assets"

    asset_id = fields.Many2one(
        'account.asset.asset', 'Asset',
        required=True, ondelete='cascade',
    )
    period_id = fields.Many2one(
        'account.period',ondelete = 'cascade',string = "Period",
        help = "Relation to a Valid Stored Period.",
        required = True,
    )
    adjust_date = start_date = fields.Date(
         string = "Adjustment Date",
        related = "period_id.date_start"
    )
    adjust_factor = fields.Float()

