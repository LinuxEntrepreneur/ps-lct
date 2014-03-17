# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
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

from openerp.osv import fields, orm
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class hr_payslip(orm.Model):
    _inherit = 'hr.payslip'

    _columns = {
        'seniority_rate': fields.function(lambda self, *args, **kwargs: self._calculate_seniority_rate(*args, **kwargs),
                                 method=True,
                                 type='float',
                                 string='Seniority rate',
                                 store=False),
        }

    def _calculate_seniority_rate(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, 0.0)
        for slip_id in ids:
            payslip = self.browse(cr, uid, slip_id, context=None)
            employee = payslip.employee_id
            # Yes, assuming all years have 365 days.
            # Also assuming the seniority is calculated w.r.t. the start date for the payslip, not the end date.
            years = (datetime.strptime(payslip.date_from, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(employee.start_date, DEFAULT_SERVER_DATE_FORMAT)).days / 365
            rate = 0.03 if years >= 3 else 0.02 if years >= 2 else 0.0
            res.update({slip_id: rate})
        return res
