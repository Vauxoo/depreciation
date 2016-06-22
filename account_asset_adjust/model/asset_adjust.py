# -*- coding: utf-8 -*-
# import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
    
    @api.v7
    def compute_depreciation_board_ext(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        currency_obj = self.pool.get('res.currency')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.value_residual == 0.0:
                continue
            posted_depreciation_line_ids = depreciation_lin_obj.search(
                cr, uid, [
                    ('asset_id', '=', asset.id), ('move_check', '=', True)
                ],order='depreciation_date desc'
            )
            old_depreciation_line_ids = depreciation_lin_obj.search(
                cr, uid, [
                    ('asset_id', '=', asset.id), ('move_id', '=', False)
                ]
            )
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(
                    cr, uid, old_depreciation_line_ids,
                    context=context
                )

            amount_to_depr = residual_amount = asset.value_residual
            if asset.prorata:
                depreciation_date = datetime.strptime(
                    self._get_last_depreciation_date(
                        cr, uid, [asset.id], context
                    )[asset.id], '%Y-%m-%d'
                )
            else:
                purchase_date = datetime.strptime(
                    asset.purchase_date, '%Y-%m-%d'
                )
                #if we already have some previous validated entries,
                #starting date is last entry + method period
                if (len(posted_depreciation_line_ids)>0):
                    last_depreciation_date = datetime.strptime(
                        depreciation_lin_obj.browse(
                            cr,uid,posted_depreciation_line_ids[0],
                            context=context
                        ).depreciation_date, '%Y-%m-%d'
                    )
                    depreciation_date = (
                        last_depreciation_date
                        + relativedelta(
                            months=+asset.method_period
                        )
                    )
                else:
                    month = purchase_date.month
                    common_period = [2,3,4,6]
                    if (asset.method_period % 12 == 0):
                        month = 1
                    elif (asset.method_period in common_period):
                        month -= (
                            (purchase_date.month - 1)
                            % asset.method_period
                        )
                    depreciation_date = datetime(
                        purchase_date.year, month, 1
                    )
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb(
                cr, uid, asset, depreciation_date, total_days, context=context
            )
            for x in range(
                len(posted_depreciation_line_ids), undone_dotation_number
            ):
                i = x + 1
                amount = self._compute_board_amount(
                    cr, uid, asset, i, residual_amount,
                    amount_to_depr, undone_dotation_number,
                    posted_depreciation_line_ids, total_days,
                    depreciation_date, context=context
                )
                residual_amount -= amount
                vals = {
                    'amount': amount,
                    'asset_id': asset.id,
                    'sequence': i,
                    'name': str(asset.id) +'/' + str(i),
                    'remaining_value': residual_amount,
                    'depreciated_value': (
                        (asset.purchase_value - asset.salvage_value)
                        - (residual_amount + amount)
                    ),
                    'depreciation_date': depreciation_date.strftime(
                        '%Y-%m-%d'
                    ),
                }
                depreciation_lin_obj.create(cr, uid, vals, context=context)
                # Considering Depr. Period as months
                depreciation_date = (
                    datetime(year, month, day)
                    + relativedelta(months=+asset.method_period)
                )
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
        return True
        


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
        return True
