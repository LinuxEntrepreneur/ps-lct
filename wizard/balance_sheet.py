# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 OpenERP (<openerp@openerp-HP-ProBook-430-G1>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from osv import fields, osv
from tools.translate import _
from xlwt import Workbook,easyxf
from xlrd import open_workbook,XL_CELL_BLANK
from xlutils.copy import copy
import StringIO
import base64
from datetime import datetime
from datetime import date, timedelta
from tempfile import TemporaryFile

class balance_sheet(osv.osv_memory):
    
    _inherit = "accounting.report"
    _name = "balance.sheet"
    
    def _getOutCell(self,outSheet, colIndex, rowIndex):
        row = outSheet._Worksheet__rows.get(rowIndex)
        if not row: return None

        cell = row._Row__cells.get(colIndex)
        return cell

    def _setOutCell(self,outSheet, col, row, value):
        
        previousCell = self._getOutCell(outSheet, col, row)
        outSheet.write(row, col, value)
        
        if previousCell:
            newCell = self._getOutCell(outSheet, col, row)
            if newCell:
                newCell.xf_idx = previousCell.xf_idx
    
 
    def _write_report(self, cr, uid, ids, context=None):
        template= open_workbook('togo/lct_finance/data/template.xls',formatting_info=True)
        report = copy(template)
        ts = template.sheet_by_index(0)
        rs = report.get_sheet(0)
        acc_ids = []
        rows = []
        for row in range(10,ts.nrows) :
            if ts.cell(row,1).ctype != XL_CELL_BLANK : 
                domain = [('code','ilike',str(ts.cell(row,1).value))]
                if not self.pool.get('account.account').search(cr, uid, domain,context=context) :
                    continue
                acc_id = self.pool.get('account.account').search(cr, uid, domain,context=context)[0]
                acc_ids.append(acc_id)
                rows.append(row)
                
        browser = self.browse(cr,uid,ids,context=context)[0]
        if browser.date_from and browser.date_to :
            context['date_from'] = browser.date_from
            context['date_to'] = browser.date_to
        elif browser.period_from and browser.period_to : 
            context['date_from'] = browser.period_from.date_start
            context['date_to'] = browser.period_from.date_end
        
        accounts = self.pool.get('account.account').browse(cr,uid,acc_ids,context=context)
        for row in rows :
            col = 3
            balance = accounts[rows.index(row)].balance
            if balance !=0 : self._setOutCell(rs, col, row, balance)
            else : self._setOutCell(rs, col, row, "")
        
        return report
        
    
    def print_report(self, cr, uid, ids, name, context=None):
        if context is None:
            context = {}
        report = self._write_report(cr,uid,ids,context=context)
        
        f = StringIO.StringIO()
        report.save(f)
        xls_file = base64.b64encode(f.getvalue())
        dlwizard = self.pool.get('balance.sheet.download').create(cr, uid, {'xls_report' : xls_file}, context=dict(context, active_ids=ids))
        return {
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'balance.sheet.download',
            'res_id': dlwizard,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': dict(context, active_ids=ids)
        }
        
