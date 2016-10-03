# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.addons.account.wizard.account_report_aged_partner_balance import account_aged_trial_balance

def _print_report(self, cr, uid, ids, data, context=None):
    res = {}
    if context is None:
        context = {}

    data = self.pre_print_report(cr, uid, ids, data, context=context)
    data['form'].update(self.read(cr, uid, ids, ['period_length', 'direction_selection'])[0])

    period_length = data['form']['period_length']
    if period_length<=0:
        raise osv.except_osv(_('User Error!'), _('You must set a period length greater than 0.'))
    if not data['form']['date_from']:
        raise osv.except_osv(_('User Error!'), _('You must set a start date.'))

    start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")

    if data['form']['direction_selection'] == 'past':
        for i in range(9)[::-1]:
            stop = start - relativedelta(days=period_length)
            res[str(i)] = {
                'name': (i!=0 and (str((9-(i+1)) * period_length) + '-' + str((9-i) * period_length)) or ('+'+str(8 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
    else:
        for i in range(9):
            stop = start + relativedelta(days=period_length)
            res[str(9-(i+1))] = {
                'name': (i!=8 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(8 * period_length))),
                'start': start.strftime('%Y-%m-%d'),
                'stop': (i!=8 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop + relativedelta(days=1)
    data['form'].update(res)
    if data.get('form',False):
        data['ids']=[data['form'].get('chart_account_id',False)]
    return {
        'type': 'ir.actions.report.xml',
        'report_name': 'aged_trial_balance',
        'datas': data
    }

# Monkeys
account_aged_trial_balance._print_report = _print_report