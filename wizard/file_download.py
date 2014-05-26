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



class liasse_fiscale_dl(osv.osv_memory):

    _name = "lct_finance.liasse.fiscale.download"

    _columns = {
            'file_name' : fields.char('File Name'),
            'xls_report' : fields.binary('Liasse Fiscale',filters='*.xls',readonly=False)
        }

    _defaults = {
        'file_name' : 'Liasse fiscale.xls'
    }

