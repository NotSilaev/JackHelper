from django.urls import reverse

from jackhelper import autodealer
from .utils import daysInYear

import datetime



class Stats:
    '''Implements methods for obtaining statistics blocks.'''

    def __init__(
        self, city: str, 
        start_date: datetime.date, 
        end_date: datetime.date,
    ):
        self.city = city
        self.start_date = start_date
        self.end_date = end_date
        self.blocks_methods = {
            'finance': self.financeBlock,
            'orders': self.ordersBlock,
            'diagnostic_packages': self.diagnosticPackagesBlock,
            'normal_hours': self.normalHoursBlock,
        }


    def getMetrics(self, block_id: str, short_output: bool = False) -> dict:
        '''Obtains and returns stats block metrics.
        
        :param block_id: statistics block id (example: "finance").
        :param short_output: if `True`, then only general metrics will be requested, without detailed ones.
        '''

        if block_id in self.blocks_methods.keys():
            connect = autodealer.getConnect(self.city)
            self.cursor = connect.cursor()

            self.short_output = short_output
            block_method = self.blocks_methods[block_id]
            block_metrics = block_method()

            connect.close()
            return {'block_id': block_id, 'metrics': block_metrics}
        else:
            raise ValueError('Unavailable block_id')


    def fetch(self, query: str, fetch_type: str, indexes: list = None, zero_if_none=False):
        return autodealer.fetch(
            cursor=self.cursor,
            query=query,
            start_date=self.start_date,
            end_date=self.end_date,
            fetch_type=fetch_type,
            indexes=indexes,
            zero_if_none=zero_if_none
        )


    def financeBlock(self) -> list:
        metrics = []
        
        works_revenue_query = '''
            SELECT SUM(SUMMA_WORK)
                FROM DOCUMENT_SERVICE_DETAIL ds
            JOIN DOCUMENT_OUT_HEADER doh
                ON ds.DOCUMENT_OUT_HEADER_ID = doh.DOCUMENT_OUT_HEADER_ID
            WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID = 11
                AND doh.STATE = 4
        '''
        works_revenue = float(self.fetch(
            works_revenue_query, 
            fetch_type='one', 
            indexes=[0], 
            zero_if_none=True
        ))
        metrics.append({
            'id': 'works_revenue', 
            'title': 'Выручка с работ', 
            'value': works_revenue, 
            'unit': '₽'
        })

        works_discount_amount_query = '''
            SELECT 
                SUM(CASE 
                    WHEN sw.TIME_VALUE IS NOT NULL
                    THEN (PRICE_NORM * TIME_VALUE * QUANTITY) * (sw.DISCOUNT_WORK / 100)

                    ELSE (PRICE * QUANTITY) * (sw.DISCOUNT_WORK / 100)
                END)
            FROM SERVICE_WORK sw
            JOIN DOCUMENT_OUT_HEADER doh
                ON sw.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
            WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID = 11
                AND doh.STATE = 4;
        '''
        works_discount_amount = float(self.fetch(
            works_discount_amount_query, 
            fetch_type='one', 
            indexes=[0], 
            zero_if_none=True
        ))
        metrics.append({
            'id': 'average_check',
            'title': 'Скидка на работы',
            'value': works_discount_amount,
            'unit': '₽',
        })  

        spare_parts_revenue_query = '''
            SELECT SUM(
                go.COST 
                * (go.GOODS_COUNT_FACT - go.GOODS_COUNT_RETURN) 
                * (1 - go.DISCOUNT / 100)
                - go.DISCOUNT_FIX
            )
                FROM GOODS_OUT go
            JOIN DOCUMENT_OUT_HEADER doh
                ON go.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
            WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID IN (2, 3, 11)
                AND STATE = 4
        '''
        spare_parts_revenue = float(self.fetch(
            spare_parts_revenue_query, 
            fetch_type='one', 
            indexes=[0], 
            zero_if_none=True
        ))
        metrics.append({
            'id': 'spare_parts_revenue', 
            'title': 'Запчасти выход',
            'value': spare_parts_revenue, 
            'unit': '₽'
        })

        revenue = works_revenue + spare_parts_revenue
        metrics.insert(0, {
            'id': 'revenue',
            'title': 'Выручка',
            'value': revenue,
            'unit': '₽',
        })  

        input_spare_parts_cost_query = '''
            SELECT SUM(
                gi.COST1 
                * (go.GOODS_COUNT_FACT) 
                - go.DISCOUNT_FIX
            )
                FROM GOODS_IN gi
            JOIN GOODS_OUT go
                ON gi.GOODS_IN_ID = go.GOODS_IN_ID
            JOIN DOCUMENT_OUT_HEADER doh
                ON go.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
            WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID IN (2, 3, 11)
                AND STATE = 4
        '''
        input_spare_parts_cost = float(self.fetch(
            input_spare_parts_cost_query, 
            fetch_type='one', 
            indexes=[0], 
            zero_if_none=True
        ))
        metrics.append({
            'id': 'input_spare_parts_cost', 
            'title': 'Запчасти вход',
            'value': input_spare_parts_cost, 
            'unit': '₽'
        })

        metrics.append({
            'id': 'input_spare_parts_cost', 
            'title': 'Доход с з/ч',
            'value': spare_parts_revenue - input_spare_parts_cost, 
            'unit': '₽'
        })

        try:
            spare_parts_margin = spare_parts_revenue / input_spare_parts_cost * 100 - 100
        except ZeroDivisionError:
            if spare_parts_revenue > 0: spare_parts_margin = 100
            else: spare_parts_margin = 0
        metrics.append({
            'id': 'spare_parts_margin', 
            'title': 'Наценка з/ч',
            'value': spare_parts_margin, 
            'unit': '%'
        })

        spare_parts_discount_amount_query = '''
            SELECT SUM(
                go.COST 
                * (go.GOODS_COUNT_FACT - go.GOODS_COUNT_RETURN) 
                * (go.DISCOUNT / 100) 
                - go.DISCOUNT_FIX
            )
            FROM GOODS_OUT go
            JOIN DOCUMENT_OUT do
                ON go.DOCUMENT_OUT_ID = do.DOCUMENT_OUT_ID
            JOIN DOCUMENT_OUT_HEADER doh
                ON do.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
            WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID IN (2, 3, 11)
                AND STATE = 4
        '''
        spare_parts_amount = self.fetch(
            spare_parts_discount_amount_query, 
            fetch_type='one', 
            indexes=[0], 
            zero_if_none=True
        )
        metrics.append({
            'id': 'average_check',
            'title': 'Скидка на з/ч',
            'value': spare_parts_amount,
            'unit': '₽',
        })   

        if self.short_output is False:
            stats_obj = Stats(self.city, self.start_date, self.end_date)
            orders_count = stats_obj.getMetrics('orders', short_output=True)['metrics'][0]['value']
            try:
                average_check = float(revenue) / orders_count
            except ZeroDivisionError:
                average_check = 0
            metrics.insert(5, {
                'id': 'average_check',
                'title': 'Средний чек',
                'value': average_check,
                'unit': '₽',
            })  

            days_in_year = daysInYear()
            last_year_stats_obj = Stats(
                self.city, 
                self.start_date-datetime.timedelta(days=days_in_year),
                self.end_date-datetime.timedelta(days=days_in_year)
            )
            last_year_metrics = last_year_stats_obj.getMetrics('finance', short_output=True)['metrics']
            last_year_revenue = last_year_metrics[0]['value']

            try:
                growth_trend = round(float(revenue) / last_year_revenue * 100 - 100, 2)
            except ZeroDivisionError:
                if revenue > 0: growth_trend = 100
                else: growth_trend = 0

            metrics.append({
                'id': 'growth_trend', 
                'title': 'Рост год к году',
                'value': growth_trend, 
                'unit': '%',
                'submetrics': last_year_metrics,
            })

        return metrics


    def ordersBlock(self) -> list:
        metrics = []

        if self.short_output:
            orders_count_query = '''
                SELECT 
                    COUNT(DISTINCT doh.DOCUMENT_OUT_HEADER_ID) AS total_orders
                FROM DOCUMENT_OUT_HEADER doh
                WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                    AND doh.DOCUMENT_TYPE_ID = 11
                    AND doh.STATE = 4
            '''
        else:
            orders_count_query = '''
                SELECT 
                    COUNT(DISTINCT doh.DOCUMENT_OUT_HEADER_ID) AS total_orders,
                    COUNT(DISTINCT CASE 
                        WHEN (ds.SPECIAL_NOTES IS NULL OR CHAR_LENGTH(ds.SPECIAL_NOTES) < 20) 
                        THEN doh.DOCUMENT_OUT_HEADER_ID 
                    END) AS orders_without_recommendations,
                    COUNT(DISTINCT CASE 
                        WHEN (ds.RUN_DURING IS NULL OR ds.RUN_BEFORE IS NULL) 
                        THEN doh.DOCUMENT_OUT_HEADER_ID 
                    END) AS orders_without_mileage,
                    COUNT(DISTINCT CASE 
                        WHEN ds.REASONS_APPEAL IS NULL 
                        THEN doh.DOCUMENT_OUT_HEADER_ID 
                    END) AS orders_without_reasons_appeal
                FROM DOCUMENT_OUT_HEADER doh
                LEFT JOIN DOCUMENT_SERVICE_DETAIL ds
                    ON doh.DOCUMENT_OUT_HEADER_ID = ds.DOCUMENT_OUT_HEADER_ID
                LEFT JOIN SERVICE_WORK sw
                    ON doh.DOCUMENT_OUT_ID = sw.DOCUMENT_OUT_ID
                WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                    AND doh.DOCUMENT_TYPE_ID = 11
                    AND doh.STATE = 4;
            '''

        orders = list(self.fetch(orders_count_query, fetch_type='one'))
        orders_count = orders[0]
        orders_count_metric = {
            'id': 'orders_count', 
            'title': 'Всего', 
            'value': orders_count, 
            'unit': 'шт.'
        }

        orders_with_discount_lte_10_query = '''
            SELECT 
                doh.DOCUMENT_OUT_HEADER_ID
            FROM DOCUMENT_OUT_HEADER doh
            JOIN DOCUMENT_OUT do
                ON doh.DOCUMENT_OUT_ID = do.DOCUMENT_OUT_ID
            JOIN SERVICE_WORK sw
                ON sw.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
            WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID = 11
                AND doh.STATE = 4
            GROUP BY doh.DOCUMENT_OUT_HEADER_ID
            HAVING FLOOR(AVG(sw.DISCOUNT_WORK)) > 0 AND FLOOR(AVG(sw.DISCOUNT_WORK)) <= 10;
        '''
        orders_with_discount_lte_10 = self.fetch(orders_with_discount_lte_10_query, fetch_type='all')
        orders.append(len(orders_with_discount_lte_10))


        if self.short_output is False:
            orders_count_metric['submetrics'] = [
                {'title': 'Без рекомендаций', 'value': orders[1], 'unit': 'шт.'},
                {'title': 'Без пробега', 'value': orders[2], 'unit': 'шт.'},
                {'title': 'Без причин обращения', 'value': orders[3], 'unit': 'шт.'},
                {'title': 'Со скидкой до 11%', 'value': orders[4], 'unit': 'шт.'},
            ]

            orders_with_discount_gte_11_query = '''
                SELECT 
                    FLOOR(AVG(sw.DISCOUNT_WORK)) AS discount_percentage,
                    COUNT(DISTINCT doh.DOCUMENT_OUT_ID) AS discount_count
                FROM DOCUMENT_OUT_HEADER doh
                JOIN SERVICE_WORK sw 
                    ON sw.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
                WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                    AND doh.DOCUMENT_TYPE_ID = 11
                    AND doh.STATE = 4
                GROUP BY doh.DOCUMENT_OUT_ID
                HAVING AVG(sw.DISCOUNT_WORK) >= 11
                ORDER BY discount_percentage;
            '''
            orders_with_discount_gte_11 = self.fetch(orders_with_discount_gte_11_query, fetch_type='all')
            orders_with_discount_gte_11_metric = {
                'id': 'orders_with_discount_gte_11', 
                'title': 'ЗН со скидкой от 11%',
                'unit': 'шт.'
            }
            orders_with_discount_gte_11_count = 0
            if orders_with_discount_gte_11:
                orders_by_percents = {}
                for order in orders_with_discount_gte_11:
                    discount_percent = int(order[0])
                    if discount_percent in orders_by_percents.keys():
                        orders_by_percents[discount_percent] += 1
                    else:
                        orders_by_percents[discount_percent] = 1

                orders_with_discount_gte_11_metric['submetrics'] = []
                for discount_percent, orders_count in orders_by_percents.items():
                    orders_with_discount_gte_11_count += orders_count
                    orders_with_discount_gte_11_metric['submetrics'].append({
                        'title': f'{discount_percent} %', 
                        'value': orders_count, 
                        'unit': 'шт.',
                        'on_click_javascript_action': f'''
                            getOrdersByPercent(
                                {discount_percent}, 
                                '{self.city}', 
                                '{self.start_date}', 
                                '{self.end_date}'
                            )
                        '''.replace('\n', '')
                    })
            orders_with_discount_gte_11_metric['value'] = orders_with_discount_gte_11_count
            metrics.append(orders_with_discount_gte_11_metric)

        metrics.insert(0, orders_count_metric)
        return metrics


    def diagnosticPackagesBlock(self) -> list:
        metrics = []

        packages_sold_query = '''
            SELECT COUNT(ds.DOCUMENT_SERVICE_DETAIL_ID)
                FROM DOCUMENT_SERVICE_DETAIL ds
            JOIN DOCUMENT_OUT_HEADER doh 
                ON ds.DOCUMENT_OUT_HEADER_ID = doh.DOCUMENT_OUT_HEADER_ID
            JOIN SERVICE_WORK sw 
                ON doh.DOCUMENT_OUT_ID = sw.DOCUMENT_OUT_ID
            WHERE ds.DATE_START BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID = 11
                AND doh.STATE = 4
                AND sw.NAME = 'Пакет диагностик при ТО';
        '''
        packages_sold = self.fetch(
            packages_sold_query, 
            fetch_type='one',
            indexes=[0],
            zero_if_none=True
        )
        metrics.append({
            'id': 'packages_sold', 
            'title': 'Продано', 
            'value': packages_sold, 
            'unit': 'шт.'
        })
        return metrics

    
    def normalHoursBlock(self) -> list:
        metrics = []

        houzs_count_query = '''
            SELECT 
                SUM(CASE 
                    WHEN sw.PRICE IS NOT NULL AND sw.TIME_VALUE IS NULL AND sw.PRICE_NORM != 0 
                    THEN (sw.PRICE / sw.PRICE_NORM)

                    WHEN sw.PRICE IS NULL AND sw.TIME_VALUE IS NOT NULL 
                    THEN (sw.TIME_VALUE * sw.QUANTITY)

                    WHEN sw.PRICE IS NOT NULL AND sw.TIME_VALUE IS NOT NULL 
                    THEN (sw.TIME_VALUE * sw.QUANTITY)

                    ELSE 0
                END) AS total_normal_hours
            FROM SERVICE_WORK sw
            JOIN DOCUMENT_OUT_HEADER doh
                ON sw.DOCUMENT_OUT_ID = doh.DOCUMENT_OUT_ID
            WHERE doh.DATE_CREATE BETWEEN timestamp '%(start_date)s 00:00' AND timestamp '%(end_date)s 23:59'
                AND doh.DOCUMENT_TYPE_ID = 11
                AND doh.STATE = 4;
        '''
        hours_count = self.fetch(
            houzs_count_query, 
            fetch_type='one',
            indexes=[0],
            zero_if_none=True
        )
        metrics.append({
            'id': 'hours_count', 
            'title': 'Всего часов', 
            'value': float(hours_count), 
            'unit': 'ч.'
        })

        return metrics