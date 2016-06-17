# -*- coding: utf-8 -*-
# import time
from datetime import datetime
# from dateutil.relativedelta import relativedelta

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


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
    adjust_date = fields.Date(
        string = "Adjustment Date",
        store = True,
        related = "period_id.date_start"
    )
    adjust_factor = fields.Float(
        string = "Adjustment Factor",
    )
    adjust_value = fields.Float(
        string = "Adjusted Value",
        digits = dp.get_precision('Account'),
    )

    _sql_constraints = [
        (
            'asset_period_combo_unique',
            'UNIQUE(asset_id, period_id)',
            "This combination of Asset and Period "
            "should not be repeated in this Table."
        ),
    ]

class AdjustableAsset(models.Model):
    _inherit = 'account.asset.asset'

    adjusted_initial_values_ids = fields.One2many(
        'account.asset.adjust.initial',
        'asset_id', string="Initial Adjustment"
    )

    @api.multi
    @api.depends('purchase_date','purchase_value')
    def adjust_initial_values(self):
        self.ensure_one()
        purchase_period = datetime.strptime(
            self.purchase_date, '%Y-%m-%d'
        ).replace(day=1)
        cpi_list = self.env['account.price.index'].search(
            [
               ("start_date", ">=", purchase_period),
            ],
            order="start_date asc",
        )
        first_idx = cpi_list[0].index_value
        for cpi in cpi_list:
            adj_factor = cpi.index_value / first_idx
            adj_value = adj_factor * self.purchase_value
            to_update = self.env['account.asset.adjust.initial'].search(
                [
                    ("asset_id", "=", self.id),
                    ("period_id", "=", cpi.period_id.id),
                ],
            )
            if to_update:
                to_update[0].write({
                    "adjust_factor": adj_factor,
                    "adjust_value": adj_value,
                })
            else:
                self.env['account.asset.adjust.initial'].create({
                    "asset_id": self.id,
                    "period_id": cpi.period_id.id,
                    "adjust_factor": adj_factor,
                    "adjust_value": adj_value,
                })
