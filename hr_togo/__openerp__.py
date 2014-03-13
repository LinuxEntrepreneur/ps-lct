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

{
    'name': 'HR Togo',
    'version': '1.0',
    'category': 'Tools',
    'description': """
HR Module for Togo
==================
    """,
    'author': 'OpenERP SA',
    'depends': ['hr_contract','hr_payroll'],
    'data': [
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'views/hr_payroll_base_wage.xml',
        'data/hr.payroll.base_wage.csv',
        'data/hr.payroll.structure.csv',
        'data/hr.salary.rule.category.csv',
        'data/hr.salary.rule.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
