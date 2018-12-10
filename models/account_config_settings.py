# -*- coding: utf-8 -*-
#  Copyright (c) 2018 - Indexa SRL. (<https://www.indexa.do/>)
#  See LICENSE file for full copyright and licensing details.

import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    l10n_do_currency_interval_unit = fields.Selection(related="company_id.l10n_do_currency_interval_unit", )
    l10n_do_currency_provider = fields.Selection(related="company_id.l10n_do_currency_provider", )
    l10n_do_currency_next_execution_date = fields.Date(related="company_id.l10n_do_currency_next_execution_date")
    currency_base = fields.Selection(related="company_id.currency_base", )

    @api.onchange('l10n_do_currency_interval_unit')
    def onchange_l10n_do_currency_interval_unit(self):
        # as the onchange is called upon each opening of the settings, we avoid overwriting
        # the next execution date if it has been already set
        if self.company_id.l10n_do_currency_next_execution_date:
            return
        if self.l10n_do_currency_interval_unit == 'daily':
            next_update = relativedelta(days=+1)
        elif self.l10n_do_currency_interval_unit == 'weekly':
            next_update = relativedelta(weeks=+1)
        elif self.l10n_do_currency_interval_unit == 'monthly':
            next_update = relativedelta(months=+1)
        else:
            self.l10n_do_currency_next_execution_date = False
            return
        self.l10n_do_currency_next_execution_date = datetime.datetime.now() + next_update

    @api.multi
    def l10n_do_update_currency_rates(self):
        companies = self.env['res.company'].browse([record.company_id.id for record in self])

        if not companies.l10n_do_update_currency_rates():
            raise UserError(_('Unable to fetch currency from given API. '
                              'The service may be temporary down. Please try again in a moment.'))