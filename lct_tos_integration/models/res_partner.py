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

    def create(self, cr, uid, vals, context=None):
        partner_id = super(res_partner, self).create(cr, uid, vals, context=context)
        self.pool.get('ftp.config').export_partners(cr, uid, [partner_id], 'create', context=context)
        return partner_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        filename = __file__.rstrip('c')
        for call in traceback.extract_stack():
            if call[0] == filename and call[2] == 'create':
                return res
        self.pool.get('ftp.config').export_partners(cr, uid, ids, 'update', context=context)
        return res