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

from report import report_sxw
from datetime import datetime,timedelta
from collections import OrderedDict

class payslip_report_pdf(report_sxw.rml_parse):
    _name = 'payslip_report_pdf'
    _description = "Employee Payslips"

    def __init__(self, cr, uid, name, context):
        super(payslip_report_pdf, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'payslips': self.get_payslip_data(cr, uid, context=context),
            'signature': self.pool.get('hr.config.settings').get_payslip_signature_big(cr, uid, name, context=context)
            })

    # Not sure how well this will perform on big data sets. The yearly stuff is
    # duplicating a ton of lookups. If it turns out this performs badly, rewrite
    # to use queries instead of ORM.
    def get_payslip_data(self, cr, uid, context=None):
        retval = OrderedDict()
        ordered_slips = {}
        payslip_obj = self.pool.get('hr.payslip')
        payslip_ids = context.get('active_ids')
        payslips = payslip_obj.browse(cr, uid, payslip_ids, context=context)

        # Customer wants their payslips ordered by employee name, alphabetically
        for payslip in payslips:
            emp_name = payslip.employee_id.name_related
            if emp_name in ordered_slips:
                ordered_slips[emp_name].append(payslip)
            else:
                ordered_slips[emp_name] = [payslip]
        payslips = []
        for employee_name in sorted(ordered_slips.keys(), key=lambda s: s.lower()):
            payslips.extend(ordered_slips[employee_name])

        for payslip in payslips:
            sen_yr, sen_mon, sen_day = self.pool.get('hr.employee')\
                .get_seniority_ymd(cr, uid, payslip.employee_id.id, context=context)
            seniority = '%dA, %dM, %dJ' % (sen_yr, sen_mon, sen_day)

            # Leaves
            leave_obj = self.pool.get('hr.holidays')
            leave_ids = leave_obj.search(cr, uid,
                [('employee_id', '=', payslip.employee_id.id)], context=context)
            leaves = leave_obj.browse(cr, uid, leave_ids, context=context)
            leaves_acquired = sum([x.number_of_days for x in leaves \
                if x.state == 'validate' \
                and x.type == 'add'\
                and x.holiday_status_id.limit == False]) or 0.0
            holidays = [x for x in leaves \
                if x.state == 'validate' \
                and x.type == 'remove' \
                and x.date_from.split()[0] >= payslip.date_from.split()[0] \
                and x.date_to.split()[0] <= payslip.date_to.split()[0]]
            # leaves_taken = sum([x.number_of_days for x in leaves \
            #     if x.state == 'validate' \
            #     and x.type == 'remove'\
            #     and x.holiday_status_id.limit == False])
            leaves_remaining = sum([x.number_of_days for x in leaves\
                if x.state == 'validate' \
                and x.holiday_status_id.limit == False]) or 0.0


            retval[payslip] = {
                # 'lines': lines,
                'seniority': seniority,
                'leaves_acquired': leaves_acquired,
                # 'leaves_taken': leaves_taken,
                'leaves_remaining': leaves_remaining,
                'holidays': holidays,
            }
            retval[payslip].update(self.get_salarial_data(cr, uid, payslip,
                yearly=False, context=context))
            # Yearly stuff
            jan_1 = payslip.date_from.split('-')[0] + '-01-01'
            slip_end = payslip.date_to.split()[0]
            yr_slip_ids = payslip_obj.search(cr, uid,
                [('employee_id', '=', payslip.employee_id.id),
                ('date_from', '>=', jan_1),
                ('date_to', '<=', slip_end)], context=context)
            yearly_data = dict.fromkeys(['gross_year',
                'salarial_costs_year',
                'patronal_costs_year',
                'net_salary_year',
                'benefits_in_kind_year',
                'worked_hours_year',
                'worked_days_year'], 0)
            for yr_slip in payslip_obj.browse(cr, uid, yr_slip_ids, context=context):
                data = self.get_salarial_data(cr, uid, yr_slip, yearly=True,
                    context=context)
                for key in data.keys():
                    yearly_data[key] += data.get(key, 0)
            retval[payslip].update(yearly_data)

        return retval

    def get_salarial_data(self, cr, uid, payslip, yearly=False, context=None):
        retval = {}
        keys = ['gross', 'salarial_costs', 'patronal_costs',
                'net_salary', 'benefits_in_kind', 'worked_hours', 'worked_days']
        lines = payslip.get_visible_lines(context=context)

        imd_model = self.pool.get('ir.model.data')
        gross_rule_id = imd_model.get_object_reference(cr, uid, 'lct_hr', 'hr_salary_rule_12')[1]
        salarial_costs_rule_id = imd_model.get_object_reference(cr, uid, 'lct_hr', 'hr_salary_rule_34')[1]
        patronal_costs_rule_id = imd_model.get_object_reference(cr, uid, 'lct_hr', 'hr_salary_rule_33')[1]
        net_salary_rule_id = imd_model.get_object_reference(cr, uid, 'lct_hr', 'hr_salary_rule_27')[1]
        benefits_in_kind_rule_id = imd_model.get_object_reference(cr, uid, 'lct_hr', 'hr_salary_rule_29')[1]
        
        resource_calendar_week_id = imd_model.get_object_reference(cr, uid, 'lct_hr', 'working_week')[1]
        resource_calendar_week = self.pool.get('resource.calendar').browse(cr, uid, resource_calendar_week_id, context=context)
        

        gross = sum(x.total for x in lines if x.salary_rule_id.id == gross_rule_id)
        salarial_costs = sum(x.total for x in lines if x.salary_rule_id.id == salarial_costs_rule_id)
        patronal_costs = sum(x.total for x in lines if x.salary_rule_id.id == patronal_costs_rule_id)
        net_salary = sum(x.total for x in lines if x.salary_rule_id.id == net_salary_rule_id)
        benefits_in_kind = sum(x.total for x in lines if x.salary_rule_id.id == benefits_in_kind_rule_id)
        # For now, it's 160h, except the 1st month, when it's prorata.
        current_day = max(datetime.strptime(payslip.date_from, '%Y-%m-%d'),datetime.strptime(payslip.employee_id.start_date, '%Y-%m-%d'))
        worked_hours = 0
        days_in_month = 0
        leaves = self.pool.get('resource.calendar')._get_leaves(cr, uid, resource_calendar_week_id, False) 
        leaves = [datetime.strptime(leave, '%Y-%m-%d') for leave in leaves]
        personal_leaves = self.pool.get('resource.calendar')._get_leaves(cr, uid, resource_calendar_week_id, payslip.employee_id.resource_id.id) 
        personal_leaves = [datetime.strptime(leave, '%Y-%m-%d') for leave in personal_leaves]

        while current_day <= datetime.strptime(payslip.date_to, '%Y-%m-%d'):
            if current_day not in set(leaves + personal_leaves):
                worked_hours += self.pool.get('resource.calendar').working_hours_on_day(cr, uid, resource_calendar_week, current_day, context=context)
                if self.pool.get('resource.calendar').working_hours_on_day(cr, uid, resource_calendar_week, current_day, context=context):
                    days_in_month += 1
            current_day += timedelta(days=1)

        # worked_hours = sum([x.number_of_hours for x in payslip.worked_days_line_ids])
        worked_days = sum([x.number_of_days for x in payslip.worked_days_line_ids])
        if not yearly:
            retval['lines'] = lines
            for key in keys:
                retval[key] = locals().get(key)
        else:
            for key in keys:
                retval[key + '_year'] = locals().get(key)
        return retval


report_sxw.report_sxw('report.webkit.payslip_report_pdf',
                      'hr.payslip',
                      'lct_hr/report/payslip_report.html.mako',
                      parser=payslip_report_pdf)
