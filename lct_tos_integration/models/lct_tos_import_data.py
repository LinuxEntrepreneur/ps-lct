

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

from openerp.osv import fields, osv
from lxml import etree as ET
import traceback
import re
from datetime import datetime


class lct_tos_import_data(osv.Model):
    _name = 'lct.tos.import.data'

    _columns = {
        'name': fields.char('File name', readonly=True),
        'content': fields.text('File content'),
        'type': fields.selection([('xml','xml')], string='File type'),
        'status': fields.selection([('fail','Failed to process'),('success','Processed'),('pending','Pending')], string='Status', readonly=True, required=True),
        'create_date': fields.date(string='Import date', readonly=True),
        'error': fields.text('Errors'),
    }

    _defaults = {
        'status': 'pending',
    }

    def button_reset(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'status': 'pending', 'error': False}, context=context)

    def process_data(self, cr, uid, ids, context=None):
        if not ids:
            return []

        imp_datas = self.browse(cr, uid, ids, context=context)
        if any((imp_data.status != 'pending') for imp_data in  imp_datas):
            raise osv.except_osv(('Error'),('You can only process pending data'))

        yac_data_ids = []
        inv_model = self.pool.get('account.invoice')
        vsl_model = self.pool.get('lct.tos.vessel')
        for imp_data in imp_datas:
            cr.execute('SAVEPOINT SP')
            filename = imp_data.name
            if re.match('^VBL_\d{6}_\d{6}\.xml$', filename):
                try:
                    inv_model.xml_to_vbl(cr, uid, imp_data.id, context=context)
                except:
                    cr.execute('ROLLBACK TO SP')
                    self.write(cr, uid, imp_data.id, {
                        'status': 'fail',
                        'error': traceback.format_exc(),
                        }, context=context)
                    continue
            elif re.match('^APP_\d{6}_\d{6}\.xml$', filename):
                try:
                    inv_model.xml_to_app(cr, uid, imp_data.id, context=context)
                except:
                    cr.execute('ROLLBACK TO SP')
                    self.write(cr, uid, imp_data.id, {
                        'status': 'fail',
                        'error': traceback.format_exc(),
                        }, context=context)
                    continue
            elif re.match('^VES_\d{6}_\d{6}\.xml$', filename):
                try:
                    vsl_model.xml_to_vessel(cr, uid, imp_data.id, context=context)
                except:
                    cr.execute('ROLLBACK TO SP')
                    self.write(cr, uid, imp_data.id, {
                        'status': 'fail',
                        'error': traceback.format_exc(),
                        }, context=context)
                    continue
            elif re.match('^VCL_\d{6}_\d{6}\.xml$', filename):
                try:
                    inv_model.xml_to_vcl(cr, uid, imp_data.id, context=context)
                except:
                    cr.execute('ROLLBACK TO SP')
                    self.write(cr, uid, imp_data.id, {
                        'status': 'fail',
                        'error': traceback.format_exc(),
                        }, context=context)
                    continue
            elif re.match('^YAC_\d{6}_\d{6}\.xml$', filename):
                yac_data_ids.append(imp_data.id)
            else:
                cr.execute('ROLLBACK TO SP')
                error = 'Filename format not known.\nKnown formats are :\n    APP_YYMMDD_SEQ000.xml\n    VBL_YYMMDD_SEQ000.xml'
                self.write(cr, uid, imp_data.id, {
                    'status': 'fail',
                    'error': error,
                    }, context=context)
                continue
            self.write(cr, uid, imp_data.id, {'status': 'success'}, context=context)
            cr.execute('RELEASE SAVEPOINT SP')

        if yac_data_ids and self.search(cr, uid, [('status','!=','success'),('id','not in',yac_data_ids)], context=context):
            error = 'Yard activities cannot be processed while other imported files are still pending or have failed to process'
            self.write(cr, uid, yac_data_ids, {
                    'status': 'fail',
                    'error': error,
                }, context=context)

        else:
            for yac_data_id in yac_data_ids:
                cr.execute('SAVEPOINT SP')
                try:
                    inv_model.xml_to_yac(cr, uid, yac_data_id, context=context)
                except:
                    cr.execute('ROLLBACK TO SP')
                    self.write(cr, uid, yac_data_id, {
                        'status': 'fail',
                        'error': traceback.format_exc(),
                        }, context=context)
                    continue
                self.write(cr, uid, yac_data_id, {'status': 'success'}, context=context)
                cr.execute('RELEASE SAVEPOINT SP')
