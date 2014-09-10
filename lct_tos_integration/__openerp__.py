# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (<http://tiny.be>).
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

{
    'name': 'LCT TOS integration',
    'author': 'OpenERP SA',
    'version': '0.1',
    'depends': ['base','account','product'],
    'category' : 'Tools',
    'summary': 'LCT TOS integration',
    'description': """
        LCT TOS integration
    """,
    'data': [
        'views/account.xml',
        'views/ftp_config.xml',
        'views/product.xml',
        'views/product_properties.xml',
        'data/product_properties.xml',
        'data/products.xml',
        'data/cron.xml',
        'data/ir_sequences.xml',
        'security/ir.model.access.csv',
        'views/lct_tos_import_data.xml',
        'data/actions.xml',
        'views/res_partner.xml',
        ],
    'images': [],
    'demo': [],
    'installable': True,
    'application' : True,
}
