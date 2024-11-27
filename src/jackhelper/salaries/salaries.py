from django.urls import reverse

from jackhelper import autodealer
from .models import SalaryMetric

import json
import datetime
import calendar
from openpyxl import Workbook
import requests


class Salaries():
    '''Implements methods for obtaining salaries blocks.'''
    
    __service_fee_percent = {
        'VLG': 0.1,
        'VLZ': 0.1,
    }
    __blocks_titles = {
        'service_consultants': 'Сервисные консультанты',
        'spare_parts_managers': 'Сотрудники ОЗЧ',
        'mechanics': 'Механики',
        'directors': 'Директора',
    }

    def __init__(self, city: str, year: int, month: int):
        self.city = city
        self.year = year
        self.month = month
        self.blocks_methods = {
            'service_consultants': self.__serviceConsultantsBlock,
            'spare_parts_managers': self.__sparePartsManagersBlock,
            'mechanics': self.__mechanicsBlock,
            'directors': self.__directorsBlock,
        }
        self.service_fee = (1 - self.__service_fee_percent[self.city])


    def getBlockData(self, block_id: str) -> dict:
        '''Obtains and returns stats block metrics.
        
        :param block_id: salaries block id (example: "service_consultants").
        '''

        if block_id in self.blocks_methods.keys():
            connect = autodealer.getConnect(self.city)
            self.cursor = connect.cursor()

            block_method = self.blocks_methods[block_id]
            block_data = block_method()

            connect.close()
            return block_data
        else:
            raise ValueError('Unavailable block_id')

    def __fetch(self, query: str, fetch_type: str, indexes: list = None, zero_if_none=False):
        start_date = datetime.datetime.strptime(
            f'{self.year}-{self.month}-1', '%Y-%m-%d'
        ).date()
        end_date = datetime.datetime.strptime(
            f'{self.year}-{self.month}-{calendar.monthrange(self.year, self.month)[1]}', '%Y-%m-%d'
        ).date()

        # start_date = datetime.datetime(2024, 11, 1).date()
        # end_date = datetime.datetime(2024, 11, 1).date()

        return autodealer.fetch(
            cursor=self.cursor,
            query=query,
            start_date=start_date,
            end_date=end_date,
            fetch_type=fetch_type,
            indexes=indexes,
            zero_if_none=zero_if_none
        )

    def __getEmployees(self, block_id):        
        employees = []
        if block_id == 'directors':
            directors_employee_ids = {
                'VLG': 96,
                'VLZ': 58,
            }
            employees_query = f'''
                SELECT DISTINCT EMPLOYEE_ID, FULLNAME
                FROM EMPLOYEE
                WHERE EMPLOYEE_ID = {directors_employee_ids[self.city]}
            '''
        else:
            jobs_ids = {
                'VLG': {
                    'service_consultants': ['4'],
                    'spare_parts_managers': ['6'],
                    'mechanics': ['5'],
                },
                'VLZ': {
                    'service_consultants': ['1'],
                    'spare_parts_managers': ['5'],
                    'mechanics': ['2', '3'],
                },
            }
            department_ids = jobs_ids[self.city][block_id]

            employees_query = f'''
                SELECT DISTINCT e.EMPLOYEE_ID, e.FULLNAME
                    FROM EMPLOYEE e
                JOIN ORGANIZATION_STRUCTURE os
                    ON e.EMPLOYEE_ID = os.EMPLOYEE_ID
                WHERE os.JOB_ID IN ({','.join(department_ids)})
            '''

        employee_id_exceptions = {
            'VLG': [42],
            'VLZ': [],
        }
        employees_raw_list = self.cursor.execute(employees_query).fetchall()
        for e in employees_raw_list:
            if e[0] not in employee_id_exceptions[self.city]:
                employees.append({
                    'id': e[0],
                    'fullname': e[1],
                })

        return employees

    def __makeEmployeeDataDict(self, employee_fullname: str, metrics_details: dict) -> dict|None:
        '''Makes a dictionary with employee data.

        :param employee_fullname: Employee fullname in AutoDealer DB.
        :param metrics_details*: Details about metrics specific to each employee block.

        `*` - if the sum of the values of `metrics_details` is zero, then the function returns `None`
        '''

        if sum(map(len, metrics_details.values())) == 0:
            return None

        employee_data = {
            'fullname': employee_fullname,
            'metrics': {
                'main': [],
                'additional': [],
            }
        }

        metrics_amount = 0

        for metric_id in metrics_details.keys():
            metric_value = 0
            metric_details = metrics_details[metric_id]
            if metric_details: 
                metric_value = sum([detail['amount'] for detail in metric_details])
            metrics_amount += metric_value
            employee_data['metrics']['main'].append({
                'id': metric_id,
                'value': metric_value,
                'details': metric_details
            })

        additional_metrics = SalaryMetric.objects.filter(
            employee=employee_fullname,
            city=self.city,
            year=self.year,
            month=self.month,
        )
        additional_metrics_amount = 0
        additional_metrics_details = []

        for metric in additional_metrics:
            match metric.metric_type:
                case 'bonus': metric_value = metric.metric_amount
                case 'deducation': metric_value = -metric.metric_amount
            additional_metrics_amount += metric_value
            employee_data['metrics']['additional'].append({
                'id': metric.id,
                'type': metric.metric_type,
                'value': metric.metric_amount,
                'comment': metric.metric_comment,
            })
            if metric.metric_comment:
                metric_description = metric.metric_comment
            else:
                metric_description = 'Без описания'
            additional_metrics_details.append({
                'description': metric_description,
                'amount': metric_value,
            })

        metrics_amount += additional_metrics_amount
        employee_data['metrics']['main'].append({
            'id': 'additional_metrics_amount',
            'value': additional_metrics_amount,
            'details': additional_metrics_details
        })
        employee_data['metrics']['main'].append({
            'id': 'amount',
            'value': metrics_amount,
        })


        return employee_data


    def getAllBlocksData(self) -> list:
        salaries_blocks_metrics = []
        for sb_id in self.blocks_methods.keys():
            salaries_blocks_metrics.append(self.getBlockData(sb_id))
        return salaries_blocks_metrics

    def __serviceConsultantsBlock(self):
        block_data = {
            'block_data': {
                'id': 'service_consultants',
                'title': 'Сервисные консультанты',
            },
            'employees': [],
            'metrics_data': [
                {'id': 'employee', 'title': 'Сотрудник'},
                {'id': 'local_works', 'title': 'Локальные работы'},
                {'id': 'spare_parts', 'title': 'Запчасти'},
                {'id': 'external_works', 'title': 'Сторонние работы'},
                {'id': 'additional_metrics_amount', 'title': 'Бонусы/вычеты'},
                {'id': 'amount', 'title': 'Сумма'},
            ],
        }

        employees = self.__getEmployees(block_id='service_consultants')
        for employee in employees:
            employee_id = employee['id']

            metrics_details = {
                'local_works': [],
                'spare_parts': [],
                'external_works': [],
            }

            # Employee works
            works_query = f'''
                SELECT
                    sw.NAME,
                    sw.PRICE, 
                    sw.TIME_VALUE, 
                    sw.QUANTITY,  
                    sw.PRICE_NORM, 
                    sw.DISCOUNT_WORK,
                    sw_ms.PARTY,
                    bs.EMPLOYEE_ID, 
                    bs.PERCENT_EXEC_WORK
                FROM SERVICE_WORK sw
                JOIN BRIGADE_STRUCTURE bs
                    ON sw.SERVICE_WORK_ID = bs.SERVICE_WORK_ID
                JOIN DOCUMENT_OUT do
                    ON sw.DOCUMENT_OUT_ID = do.DOCUMENT_OUT_ID
                JOIN DOCUMENT_OUT_HEADER doh
                    ON do.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
                JOIN SERVICE_WORK_MANAGER_STRUCTURE sw_ms
                    ON sw.SERVICE_WORK_ID = sw_ms.SERVICE_WORK_ID
                JOIN MANAGER m
                    ON sw_ms.MANAGER_ID = m.MANAGER_ID
                JOIN ORGANIZATION_STRUCTURE os
                    ON m.ORGANIZATION_STRUCTURE_ID = os.ORGANIZATION_STRUCTURE_ID
                WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                    AND doh.DOCUMENT_TYPE_ID = 11
                    AND doh.STATE = 4
                    AND os.EMPLOYEE_ID = {employee_id};
            '''
            works = self.__fetch(
                works_query, 
                fetch_type='all'
            )

            for work in works:
                name = work[0]
                price = work[1]
                time_value = work[2]
                quantity = work[3]
                price_norm = work[4]
                discount = work[5]
                manager_party = work[6]
                worker_employee_id = work[7]
                worker_percent_exec_work = work[8]

                discount = (1 - discount / 100)
                if time_value:
                    work_price = round((float(price_norm) * float(time_value) * quantity) * discount, 2)
                else:
                    work_price = round((float(price) * quantity) * discount, 2)

                # Calculation employee work profit for external work
                if worker_employee_id is None:
                    external_work_price_part = work_price * (worker_percent_exec_work / 100)

                    if external_work_price_part == 0: 
                        continue
                
                    if True in list(map(lambda item: item in name.lower(), ['прошивка', 'стекл', 'сигнал'])):
                        employee_percent = 0.25
                    else:
                        employee_percent = 0.5

                    work_total_profit = (
                        (work_price - external_work_price_part) * self.service_fee
                    )
                    employee_work_profit = work_total_profit * employee_percent * manager_party
                    metrics_details['external_works'].append({
                        'description': name,
                        'amount': employee_work_profit,
                    })
                    continue

                # Calculation employee work profit for local work
                employee_percent = 0.1
                employee_work_profit = work_price * self.service_fee * employee_percent * manager_party
                metrics_details['local_works'].append({
                    'description': name,
                    'amount': employee_work_profit,
                })


            # Employee spare_parts
            spare_parts_query = f'''
                SELECT 
                    sn.FULLNAME,
                    gi.COST1,
                    go.COST,
                    go.GOODS_COUNT_FACT,
                    go.DISCOUNT,
                    go.DISCOUNT_FIX,
                    go.GOODS_COUNT_RETURN
                FROM GOODS_OUT go
                JOIN GOODS_IN gi
                    ON gi.GOODS_IN_ID = go.GOODS_IN_ID
                JOIN SHOP_NOMENCLATURE sn
                    ON go.SHOP_NOMENCLATURE_ID = sn.SHOP_NOMENCLATURE_ID
                JOIN GOODS_OUT_MANAGER_STRUCTURE go_ms
                    ON go.GOODS_OUT_ID = go_ms.GOODS_OUT_ID
                JOIN MANAGER m
                    ON go_ms.MANAGER_ID = m.MANAGER_ID
                JOIN ORGANIZATION_STRUCTURE os
                    ON m.ORGANIZATION_STRUCTURE_ID = os.ORGANIZATION_STRUCTURE_ID
                    AND os.EMPLOYEE_ID = {employee_id}
                JOIN DOCUMENT_OUT_HEADER doh
                    ON go.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
                    AND doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                    AND doh.DOCUMENT_TYPE_ID IN (2, 3, 11)
                    AND doh.STATE = 4
            '''
            spare_parts = self.__fetch(
                spare_parts_query, 
                fetch_type='all'
            )
            for spare_part in spare_parts:
                name = spare_part[0]
                purchase_price = float(spare_part[1])
                sale_price = float(spare_part[2])
                count = float(spare_part[3])
                discount = spare_part[4]
                discount_fix = float(spare_part[5])
                count_return = float(spare_part[6])

                if name.lower() == 'расходные материалы':
                    continue

                # Calculation employee spare part profit
                spare_part_revenue = round(
                    sale_price 
                    * (count - count_return) 
                    *  (1 - discount / 100)
                    - (purchase_price * count) 
                    - discount_fix
                , 2)
                employee_percent = 0.25
                employee_spare_part_profit = spare_part_revenue * employee_percent
                metrics_details['spare_parts'].append({
                    'description': name,
                    'amount': employee_spare_part_profit,
                })

            employee_data = self.__makeEmployeeDataDict(employee['fullname'], metrics_details)
            if employee_data:
                block_data['employees'].append(employee_data)

        return block_data

    def __sparePartsManagersBlock(self):
        block_data = {
            'block_data': {
                'id': 'spare_parts_managers',
                'title': 'Сотрудники ОЗЧ',
            },
            'employees': [],
            'metrics_data': [
                {'id': 'employee', 'title': 'Сотрудник'},
                {'id': 'spare_parts', 'title': 'Запчасти'},
                {'id': 'good_receipts', 'title': 'Товарные чеки'},
                {'id': 'external_works', 'title': 'Сторонние работы'},
                {'id': 'additional_metrics_amount', 'title': 'Бонусы/вычеты'},
                {'id': 'amount', 'title': 'Сумма'},
            ],
        }
        
        spare_parts_revenue = 0
        good_receipts_revenue = 0
        external_works_revenue = 0


        # Spare parts revenue
        spare_parts_query = f'''
            SELECT 
                sn.FULLNAME,
                gi.COST1,
                go.COST,
                go.GOODS_COUNT_FACT,
                go.DISCOUNT,
                go.DISCOUNT_FIX,
                go.GOODS_COUNT_RETURN,
                doh.DOCUMENT_TYPE_ID
            FROM GOODS_OUT go
            JOIN GOODS_IN gi
                ON gi.GOODS_IN_ID = go.GOODS_IN_ID
            JOIN SHOP_NOMENCLATURE sn
                ON go.SHOP_NOMENCLATURE_ID = sn.SHOP_NOMENCLATURE_ID
            JOIN DOCUMENT_OUT_HEADER doh
                ON go.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
                AND doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID IN (2, 3, 11)
                AND doh.STATE = 4
        '''
        spare_parts = self.__fetch(
            spare_parts_query, 
            fetch_type='all'
        )
        for spare_part in spare_parts:
            name = spare_part[0]
            purchase_price = float(spare_part[1])
            sale_price = float(spare_part[2])
            count = float(spare_part[3])
            discount = spare_part[4]
            discount_fix = float(spare_part[5])
            count_return = float(spare_part[6])
            document_type_id = spare_part[7]

            if name.lower() == 'расходные материалы':
                continue

            # Calculation employee spare part profit
            spare_part_revenue = round(
                sale_price 
                * (count - count_return) 
                *  (1 - discount / 100)
                - (purchase_price * count) 
                - discount_fix
            , 2)
            department_percent = 0.3
            spare_part_profit = spare_part_revenue * department_percent
            
            if document_type_id == 11:
                spare_parts_revenue += spare_part_profit
            elif document_type_id in [2,3]:
                good_receipts_revenue += spare_part_profit


        # External works revenue
        external_works_query = f'''
            SELECT
                sw.PRICE, 
                sw.TIME_VALUE, 
                sw.QUANTITY,  
                sw.PRICE_NORM, 
                sw.DISCOUNT_WORK,
                bs.PERCENT_EXEC_WORK
            FROM SERVICE_WORK sw
            JOIN BRIGADE_STRUCTURE bs
                ON sw.SERVICE_WORK_ID = bs.SERVICE_WORK_ID
            JOIN DOCUMENT_OUT do
                ON sw.DOCUMENT_OUT_ID = do.DOCUMENT_OUT_ID
            JOIN DOCUMENT_OUT_HEADER doh
                ON do.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
            WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID = 11
                AND doh.STATE = 4
                AND bs.EMPLOYEE_ID IS NULL;
        '''
        external_works = self.__fetch(
            external_works_query, 
            fetch_type='all'
        )

        for work in external_works:
            price = work[0]
            time_value = work[1]
            quantity = work[2]
            price_norm = work[3]
            discount = work[4]
            worker_percent_exec_work = work[5]

            discount = (1 - discount / 100)
            if time_value:
                work_price = round((float(price_norm) * float(time_value) * quantity) * discount, 2)
            else:
                work_price = round((float(price) * quantity) * discount, 2)

            external_work_price_part = work_price * (worker_percent_exec_work / 100)

            if external_work_price_part == 0: 
                continue
        
            if True in list(map(lambda item: item in name.lower(), [
                'прошивка', 'стекл', 'кодировка', 'мойка'
            ])):
                continue

            department_percent = 0.3
            department_work_profit = (
                (work_price - external_work_price_part) * department_percent * self.service_fee
            )
            external_works_revenue += department_work_profit

        if (spare_parts_revenue + good_receipts_revenue + external_works_revenue) > 0:
            employees = self.__getEmployees(block_id='spare_parts_managers')
            for employee in employees:
                employee_id = employee['id']

                metrics_details = {
                    'spare_parts': [
                        {'description': 'Без описания', 'amount': spare_parts_revenue / len(employees)}
                    ],
                    'good_receipts': [
                        {'description': 'Без описания', 'amount': good_receipts_revenue / len(employees)}
                    ],
                    'external_works': [
                        {'description': 'Без описания', 'amount': external_works_revenue / len(employees)}
                    ],
                }
                employee_data = self.__makeEmployeeDataDict(employee['fullname'], metrics_details)
                if employee_data:
                    block_data['employees'].append(employee_data)

        return block_data

    def __mechanicsBlock(self):
        block_data = {
            'block_data': {
                'id': 'mechanics',
                'title': 'Механики',
            },
            'employees': [],
            'metrics_data': [
                {'id': 'employee', 'title': 'Сотрудник'},
                {'id': 'standard_hours', 'title': 'Обычные часы'},
                {'id': 'aggregate_hours', 'title': 'Агрегатные часы'},
                {'id': 'reworked_hours', 'title': 'Часы переработок'},
                {'id': 'additional_metrics_amount', 'title': 'Бонусы/вычеты'},
                {'id': 'amount', 'title': 'Сумма'},
            ],
        }

        hours_tariff = {
            'VLG': {
                'standard': 330,
                'rework': 430,
            },
            'VLZ': {
                'standard': 480,
                'rework': 480,
            },
        }

        employees = self.__getEmployees(block_id='mechanics')
        for employee in employees:
            employee_id = employee['id']

            metrics_details = {
                'standard_hours': [],
                'aggregate_hours': [],
                'reworked_hours': [],
            }

            # Mechanic salary
            works_query = f'''
                SELECT
                    sw.NAME,
                    sw.PRICE, 
                    sw.TIME_VALUE, 
                    sw.QUANTITY,  
                    sw.PRICE_NORM,
                    bs.PERCENT_EXEC_WORK,
                    bs.PERCENT_WORK_PARTY,
                    bs.TARIFF,
                    (SELECT COUNT(DISTINCT bs_inner.EMPLOYEE_ID)
                    FROM BRIGADE_STRUCTURE bs_inner
                    WHERE bs_inner.SERVICE_WORK_ID = sw.SERVICE_WORK_ID) AS EMPLOYEE_COUNT
                FROM SERVICE_WORK sw
                JOIN BRIGADE_STRUCTURE bs
                    ON sw.SERVICE_WORK_ID = bs.SERVICE_WORK_ID
                JOIN DOCUMENT_OUT do
                    ON sw.DOCUMENT_OUT_ID = do.DOCUMENT_OUT_ID
                JOIN DOCUMENT_OUT_HEADER doh
                    ON do.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
                WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                    AND doh.DOCUMENT_TYPE_ID = 11
                    AND doh.STATE = 4
                    AND bs.EMPLOYEE_ID = {employee_id};

            '''
            works = self.__fetch(
                works_query, 
                fetch_type='all'
            )

            employee_work_time = 0
            for work in works:
                name = work[0]
                price = work[1]
                time_value = work[2]
                quantity = work[3]
                price_norm = work[4]
                worker_percent_exec_work = work[5]
                worker_percent_work_party = work[6]
                worker_tariff = work[7]
                worker_count = work[8]

                employee_hours_tariff = hours_tariff[self.city]['standard']

                if worker_percent_exec_work > 0:
                    work_price_part = (worker_percent_exec_work / 100) * (float(price_norm) * self.service_fee)
                elif worker_percent_exec_work == 0 and worker_tariff == 0:
                    work_price_part = employee_hours_tariff
                else:
                    work_price_part = worker_tariff


                standard_hours = 0
                aggregate_hours = 0

                if time_value:
                    time_value = float(time_value)
                else:
                    time_value = float(price / price_norm)

                if self.city == 'VLG':
                    if worker_percent_work_party > 0:
                        if work_price_part <= employee_hours_tariff:
                            standard_hours += time_value * quantity * (worker_percent_work_party / 100)
                        if work_price_part > employee_hours_tariff:
                            aggregate_hours += time_value * quantity * (worker_percent_work_party / 100)
                    else:
                        if work_price_part <= employee_hours_tariff:
                            standard_hours += time_value * quantity / workers_count
                        if work_price_part > employee_hours_tariff:
                            aggregate_hours += time_value * quantity / workers_count

                elif self.city == 'VLZ':
                    if worker_percent_work_party > 0:
                        if (work_price_part <= employee_hours_tariff) or (work_price_part > employee_hours_tariff):
                            standard_hours += time_value * quantity * (worker_percent_work_party / 100)
                    else:
                        if (work_price_part <= employee_hours_tariff) or (work_price_part > employee_hours_tariff):
                            aggregate_hours += time_value * quantity / workers_count

                employee_work_time += (standard_hours+aggregate_hours)
                if 0 < employee_work_time < 150:
                    standard_hours_profit = standard_hours * work_price_part
                    aggregate_hours_profit = aggregate_hours * work_price_part
                    metrics_details['standard_hours'].append({
                        'description': name,
                        'amount': standard_hours_profit,
                    })
                    metrics_details['aggregate_hours'].append({
                        'description': name,
                        'amount': aggregate_hours_profit,
                    })
                elif employee_work_time >= 150:
                    reworked_hours_profit = (standard_hours+aggregate_hours)*hours_tariff[self.city]['rework']
                    metrics_details['reworked_hours'].append({
                        'description': name,
                        'amount': reworked_hours_profit,
                    })

            employee_data = self.__makeEmployeeDataDict(employee['fullname'], metrics_details)
            if employee_data:
                block_data['employees'].append(employee_data)

        return block_data

    def __directorsBlock(self):
        employee = self.__getEmployees(block_id='directors')[0]

        block_data = {
            'block_data': {
                'id': 'directors',
                'title': 'Директора',
            },
            'employees': [],
            'metrics_data': [
                {'id': 'employee', 'title': 'Сотрудник'},
                {'id': 'normal_hours', 'title': 'Нормо-часы'},
                {'id': 'works', 'title': 'Собственные работы'},
                {'id': 'additional_salary', 'title': 'Доп. мотивация'},
                {'id': 'additional_metrics_amount', 'title': 'Бонусы/вычеты'},
                {'id': 'amount', 'title': 'Сумма'},
            ],
        }

        metrics_details = {
            'normal_hours': [],
            'works': [],
            'additional_salary': [],
        }

        # Get current month plan
        response = requests.get(f'''
            http://localhost:8000/
            plans/api/getPlanMetrics/
            ?city={self.city}&year={self.year}&month={self.month}
        '''.replace('\n', '').replace(' ', ''))
        metrics = json.loads(response.text)['metrics']


        # Get external works hours
        external_works_hours_query = f'''
            SELECT DISTINCT SUM((sw.PRICE / sw.PRICE_NORM) * sw.QUANTITY)
            FROM SERVICE_WORK sw
            JOIN BRIGADE_STRUCTURE bs
                ON sw.SERVICE_WORK_ID = bs.SERVICE_WORK_ID
            JOIN DOCUMENT_OUT do
                ON sw.DOCUMENT_OUT_ID = do.DOCUMENT_OUT_ID
            JOIN DOCUMENT_OUT_HEADER doh
                ON do.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
            WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID = 11
                AND doh.STATE = 4
                AND bs.EMPLOYEE_ID IS NULL;
        '''
        external_works_hours = self.__fetch(
            external_works_hours_query, 
            fetch_type='one',
            indexes=[0],
            zero_if_none=True,
        )


        if self.city == 'VLG':
            minimum_salary = 65_000

            # Normal hours salary
            response = requests.get(f'''
                http://localhost:8000/
                plans/api/getPlanMetrics/
                ?city={self.city}&year={self.year}&month={self.month}
            '''.replace('\n', '').replace(' ', ''))

            metrics = json.loads(response.text)['metrics']
            spare_parts = metrics[2]
            normal_hours = metrics[3]

            current_normal_hours = int(normal_hours['current_value']) - int(external_works_hours)

            if current_normal_hours < 900:
                normal_hours_tariff = 35
            elif 900 < current_normal_hours < 1150:
                normal_hours_tariff = 45
            elif 1150 < current_normal_hours < 1350:
                normal_hours_tariff = 50
            elif current_normal_hours > 1350:
                normal_hours_tariff = 55

            spare_parts_tariff = 10

            normal_hours_salary = (normal_hours_tariff + spare_parts_tariff) * current_normal_hours
            if normal_hours_salary < minimum_salary:
                normal_hours_salary = minimum_salary
            metrics_details['normal_hours'].append({
                'description': f'{current_normal_hours} ч.',
                'amount': normal_hours_salary,
            })

            # Additional salary
            spare_parts_plan_overfulfill_percentage = int(
                (spare_parts['current_value'] / spare_parts['plan_value'] * 100) - 100
            )
            if spare_parts_plan_overfulfill_percentage >= 25:
                spare_parts_plan_overfulfill_bonus = 10_000

                if spare_parts_plan_overfulfill_percentage >= 50:
                    spare_parts_plan_overfulfill_bonus = 15_000
                elif spare_parts_plan_overfulfill_percentage >= 90:
                    spare_parts_plan_overfulfill_bonus = 20_000

                metrics_details['additional_salary'].append({
                    'description': f'Перевыполнение плана по з/ч на {spare_parts_plan_overfulfill_percentage}%',
                    'amount': spare_parts_plan_overfulfill_bonus,
                })


        elif self.city == 'VLZ':
            minimum_salary = 50_000
            metrics_details['normal_hours'].append({
                'description': f'Несгораемая сумма',
                'amount': minimum_salary,
            })

            # Normal hours salary
            normal_hours = metrics[3]

            current_normal_hours = int(normal_hours['current_value'])
            normal_hours_tariff = 40

            normal_hours_salary = normal_hours_tariff * current_normal_hours
            metrics_details['normal_hours'].append({
                'description': f'{current_normal_hours} ч.',
                'amount': normal_hours_salary,
            })

            # Mechanic salary
            works_query = f'''
                SELECT
                    sw.NAME,
                    sw.PRICE, 
                    sw.TIME_VALUE, 
                    sw.QUANTITY,  
                    sw.PRICE_NORM,
                    bs.PERCENT_EXEC_WORK,
                    bs.TARIFF
                FROM SERVICE_WORK sw
                JOIN BRIGADE_STRUCTURE bs
                    ON sw.SERVICE_WORK_ID = bs.SERVICE_WORK_ID
                JOIN DOCUMENT_OUT do
                    ON sw.DOCUMENT_OUT_ID = do.DOCUMENT_OUT_ID
                JOIN DOCUMENT_OUT_HEADER doh
                    ON do.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
                WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                    AND doh.DOCUMENT_TYPE_ID = 11
                    AND doh.STATE = 4
                    AND bs.EMPLOYEE_ID = {employee['id']};
            '''
            works = self.__fetch(
                works_query, 
                fetch_type='all'
            )

            for work in works:
                name = work[0]
                price = work[1]
                time_value = work[2]
                quantity = work[3]
                price_norm = work[4]
                worker_percent_exec_work = work[5]
                worker_tariff = work[6]

                if time_value:
                    work_profit = (float(time_value) * quantity) * worker_tariff
                else:
                    work_profit = (float(price) / float(price_norm) * quantity) * worker_tariff
                metrics_details['works'].append({
                    'description': name,
                    'amount': work_profit,
                })


        employee_data = self.__makeEmployeeDataDict(employee['fullname'], metrics_details)
        if employee_data:
            block_data['employees'].append(employee_data)

        return block_data