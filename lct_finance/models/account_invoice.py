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

from openerp.osv import fields, orm, osv
from openerp.tools.translate import _

REPORT_TITLE = [
    ('out_invoice','Invoice'),
    ('in_invoice','Invoice'),
    ('out_refund','Credit Note'),
    ('in_refund','Debit Note'),
    ]

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def _get_report_title(self, cr, uid, ids, name, arg, context=None):
        return {invoice.id: invoice.type for invoice in self.browse(cr, uid, ids, context=context)}

    def _get_report_title_value(self, cr, uid, ids, lang, context=None):
        titles = {k:v for k,v in REPORT_TITLE}
        invoice = self.browse(cr, uid, ids[0], context=context)
        src = titles.get(invoice.report_title if invoice else None, '')
        name = 'account.invoice,report_title'
        translation_id = self.pool.get('ir.translation').search(cr, uid, [
            ('src', '=', src),
            ('lang', '=', lang),
            ('name', '=', name)
            ], context=context, limit=1)
        if translation_id:
            return self.pool.get('ir.translation').browse(cr, uid, translation_id[0], context=context).value
        return src

    _columns = {
        'bank': fields.char('Bank', size=64),
        'bank_bic': fields.char('Swift', size=64),
        'iban': fields.char('IBAN', size=64),
        'bank_code': fields.char('Bank Code', size=64),
        'counter_code': fields.char('Counter Code', size=64),
        'acc_number': fields.char('Account Number', size=64),
        'rib': fields.char('RIB', size=64),
        'customer_nbr': fields.char('Customer Number', size=64),
        'reference' : fields.text('Reference'),
        # For the invoice report (fiche d'imputation)
        'create_date': fields.datetime('Creation Date' , readonly=True),
        'report_title': fields.function(_get_report_title, type='selection', selection=REPORT_TITLE, string='Report Title', store=True),
    }

    def action_move_create(self, cr, uid, ids, context=None):
        invoice_line_model = self.pool.get('account.invoice.line')
        for invoice in self.browse(cr, uid, ids, context=context):
            for line in invoice.invoice_line:
                if line.invoice_line_tax_id or not line.product_id:
                    continue
                if line.product_id.vat_free_income_account_id:
                    invoice_line_model.write(cr, uid, [line.id], {'account_id': line.product_id.vat_free_income_account_id.id}, context=context)
                elif line.product_id.categ_id and line.product_id.categ_id.vat_free_income_account_id:
                    invoice_line_model.write(cr, uid, [line.id], {'account_id': line.product_id.categ_id.vat_free_income_account_id.id}, context=context)
        return super(account_invoice, self).action_move_create(cr, uid, ids, context=context)

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=context)
        res.update({"name": x['name']})
        line = self.pool.get('account.invoice.line').browse(cr, uid, x.get('invl_id'), context=context)
        if line and line.asset_id:
            res.update({"to_update_asset_id": line.asset_id.id})
        return res

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context)
        res['name'] = line.name.split('\n')[0]
        return res