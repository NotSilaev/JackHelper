from jackhelper import autodealer

import datetime


def getOrdersCountAndList(
    city: str, 
    start_date: datetime.datetime, 
    end_date: datetime.datetime, 
    search: str, 
    tags: tuple, 
    offset: int, 
    page: int
) -> tuple[int, list]:
    '''Creates a tuple with the number of orders and their list.
    
    :param city: city code in uppercase (example: "VLG").
    :param start_date: the start date for the selection from the range.
    :param end_date: the end date for the selection from the range.
    :param search: text from "search" input.
    :param tags: tuple of orders tags.
    :param offset: number of orders which must be loaded.
    :param page: current page number.
    '''

    orders = []
    where_conditions, having_conditions, params_values = makeQueryConditionsList(search, tags)

    connect = autodealer.getConnect(city)
    cursor = connect.cursor()
    orders_list_query = '''
        SELECT doh.FULLNUMBER, 
            doh.DATE_CREATE, 
            c.FULLNAME, 
            FLOOR(AVG(sw.DISCOUNT_WORK)) AS AVG_DISCOUNT_WORK
        FROM DOCUMENT_OUT_HEADER doh
        LEFT JOIN DOCUMENT_SERVICE_DETAIL ds
            ON doh.DOCUMENT_OUT_HEADER_ID = ds.DOCUMENT_OUT_HEADER_ID
        LEFT JOIN DOCUMENT_OUT do 
            ON doh.DOCUMENT_OUT_ID = do.DOCUMENT_OUT_ID
        LEFT JOIN SERVICE_WORK sw 
            ON doh.DOCUMENT_OUT_ID = sw.DOCUMENT_OUT_ID
        JOIN CLIENT c 
            ON do.CLIENT_ID = c.CLIENT_ID
        WHERE (doh.DATE_CREATE BETWEEN timestamp '{start_date} 00:00' AND timestamp '{end_date} 23:59')
            AND doh.DOCUMENT_TYPE_ID = 11
            AND doh.STATE = 4
            {where_conditions}
        GROUP BY doh.FULLNUMBER, doh.DATE_CREATE, c.FULLNAME
        {having_conditions}
        ORDER BY doh.DATE_CREATE
    '''.format(
        start_date=start_date, 
        end_date=end_date,
        where_conditions=("AND " + "\nAND ".join(where_conditions) if where_conditions else ''),  
        having_conditions=("HAVING " + "\nAND ".join(having_conditions) if having_conditions else ''),  
    )
    raw_orders = cursor.execute(orders_list_query, params_values).fetchall()
    connect.close()

    orders_count = len(raw_orders)
    if page > 0:
        row_start = 0 + offset * (page-1)
        row_end = row_start + offset
        if orders_count < row_start:
            row_start = 0
            row_end = offset
    else:
        row_start = 0
        row_end = len(raw_orders)

    for order in raw_orders[row_start:row_end]:
        fullnumber = order[0]
        date = order[1].date()
        client_fullname = order[2]
        discount_work = order[3]
        orders.append({
            'fullnumber': fullnumber,
            'date': date,
            'metrics': [
                {'title': 'Клиент', 'value': client_fullname},
                {'title': 'Скидка', 'value': discount_work, 'unit': '%'},
            ],
        })
        
    return orders_count, orders


def makeQueryConditionsList(search, tags) -> tuple[list, list, list]:
    '''Creates a list of conditions for SQL orders selection query based on search and tags.'''

    where_conditions, having_conditions, params_values = [], [], []

    if search:
        if len(search) > 21:
            raise ValueError('Максимальная длина поискового запроса - 21 символ.')
        search_condition = "(doh.FULLNUMBER LIKE '%' || ? || '%')"
        where_conditions.append(search_condition)
        params_values.append(search.upper())

    if tags:
        tags_conditions = {
            'without_recommendations': {
                "condition": "(ds.SPECIAL_NOTES IS NULL OR CHAR_LENGTH(ds.SPECIAL_NOTES) < 20)",
                "sql_block": "WHERE"
            },
            'without_milleage': {
                "condition": "(ds.RUN_DURING IS NULL OR ds.RUN_BEFORE IS NULL)",
                "sql_block": "WHERE"
            },
            'without_reasons_appeal': {
                "condition": "(ds.REASONS_APPEAL IS NULL)",
                "sql_block": "WHERE"
            },
            'with_discount_lte_10': {
                "condition": "FLOOR(AVG(sw.DISCOUNT_WORK)) > 0 AND FLOOR(AVG(sw.DISCOUNT_WORK)) <= 10",
                "sql_block": "HAVING"
            },
            'with_discount_gte_11': {
                "condition": "FLOOR(AVG(sw.DISCOUNT_WORK)) >= 11",
                "sql_block": "HAVING"
            },
        }
        for tag in tags:
            if tag in tags_conditions.keys(): 
                tag_data = tags_conditions[tag]
                match tag_data['sql_block']:
                    case 'WHERE': where_conditions.append(tag_data['condition'])
                    case 'HAVING': having_conditions.append(tag_data['condition'])

    return where_conditions, having_conditions, params_values