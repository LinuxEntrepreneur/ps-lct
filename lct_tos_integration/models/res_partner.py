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
from datetime import datetime, timedelta
import traceback

class res_partner(osv.Model):
    _inherit = 'res.partner'

    def _calc_generic_customer(self, cr, uid, ids, fields, arg, context=None):
        generic_customer_id = self.pool.get('ir.model.data').get_record_id(cr, uid, 'lct_tos_integration', 'lct_generic_customer', context=context)
        return {partner_id: (partner_id == generic_customer_id) for partner_id in ids}

    _columns = {
        'ref': fields.char('Customer key', size=64, select=1, required=True),
        'tax_id': fields.many2one('account.tax', string="Tax"),
        'sync': fields.boolean('Synchronize', help='Synchronize this customer with FTP server when it is updated'),
        'generic_customer': fields.function(_calc_generic_customer, type='boolean', string="Is generic customer"),
    }

    def _default_ref(self, cr, uid, context=None):
        return self.pool.get('ir.sequence').next_by_code(cr, uid, 'lct_sequence_partner_ref', context=context)

    _defaults = {
        'ref': _default_ref,
        'sync': True,
    }

    def create(self, cr, uid, vals, context=None):
        partner_id = super(res_partner, self).create(cr, uid, vals, context=context)
        partner = self.browse(cr, uid, partner_id, context=context)
        if partner.customer and partner.sync:
            self.pool.get('lct.tos.export.data').export_partners(cr, uid, [partner_id], context=context)
        return partner_id

    def button_export_partner(self, cr, uid, ids, context=None):
        self.pool.get('lct.tos.export.data').export_partners(cr, uid, ids, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)

        filename = __file__.rstrip('c')
        for call in traceback.extract_stack():
            if call[0] == filename and call[2] == 'create':
                return res

        sync_customer_ids = self.search(cr, uid, [('id', 'in', ids), ('customer', '=', True), ('sync', '=', True)], context=context)
        if not sync_customer_ids:
            return res

        to_update = [
            'name',
            'ref',
            'street',
            'street2',
            'city',
            'zip',
            'country_id',
            'email',
            'website',
            'phone',
        ]
        if any(item in vals for item in to_update):
            self.pool.get('lct.tos.export.data').export_partners(cr, uid, sync_customer_ids, context=context)
        elif 'mobile' in vals:
            for partner in self.browse(cr, uid, sync_customer_ids, context=context):
                if not partner.phone:
                    self.pool.get('lct.tos.export.data').export_partners(cr, uid, [partner.id], context=context)
        return res
