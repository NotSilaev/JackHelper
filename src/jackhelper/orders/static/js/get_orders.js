$(document).ready(function() {
    getOrders();
});

function getOrders(city, start_date, end_date, tags, search, page) {
    endpoint_url = location.href + 'api/getOrders/'
    return $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: {
            city: city,
            start_date: start_date,
            end_date: end_date,
            tags: JSON.stringify(tags),
            search: search,
            page: page,
        },

        success: function(response) {
            setPaginator(response['pagination']);
            addOrdersCards(response['orders']);
        },

        error: function(response) {
            exceptionsHandler(response.responseJSON);
        }
    });
}

function setPaginator(pagination_data) {
    let pages_count = pagination_data['pages_count'];
    let current_page = pagination_data['current_page'];

    if (pages_count <= 1) {
        return false;
    };

    var pagination_block = $('.pagination');
    pagination_block.empty();

    pagination_block.append('<ul id="pages-list"></ul>');
    var pages_list = $('#pages-list');

    function getPageFrame(page, page_id) {
        if (page_id === undefined) {page_id = page};
        let page_frame = `
            <li>
                <button id="page-${page_id}" onclick="setCurrentPage(${page_id})">
                ${page}
                </button>
            </li>
        `
        return page_frame;
    }

    if (current_page > 1) {
        pages_list.append(getPageFrame('Назад', page_id=current_page-1));
    }
    
    let start_page = Math.max(1, current_page - 3);
    let end_page = Math.min(pages_count, current_page + 3);
    
    for (let p = start_page; p <= end_page; p++) {
        pages_list.append(getPageFrame(p));
    
        if (p === current_page) {
            pages_list.find('#page-' + p).addClass('current-page');
        }
    }
    
    if (current_page < pages_count) {
        pages_list.append(getPageFrame('Далее', page_id=current_page+1));
    }
}

function addOrdersCards(orders_data) {
    let orders_count = orders_data['count'];
    var orders_list = $('#orders-list');
    orders_list.empty();

    if (orders_count === 0) {
        orders_list.append('<h3>Нет ни одного заказ-наряда</h3>')
        return false;
    };
    
    let orders = orders_data['list'];
    orders.forEach(order => {
        let fullnumber = order['fullnumber'];
        let date = order['date'];
        let metrics = order['metrics'];

        orders_list.append(`
            <li id='${fullnumber}'
                class='order-block'
                onclick='showOrderWindow("${fullnumber}", ${JSON.stringify(metrics)})'
            >
                <div class="order-data">
                    <h2>#${fullnumber}</h2>
                    <p>${date}</p>
                </div>
                <div class="order-metrics"></div>
            </li>
        `)

        if (metrics) {
            var order_metrics_list = orders_list.find('#' + fullnumber + ' ' + '.order-metrics');
            metrics.forEach(metric => {
                unit = metric['unit'];
                if (unit === undefined) {
                    unit = '';
                };
                order_metrics_list.append(`
                    <p>
                        ${metric['title']}
                        <span class="truncate-text" title='${metric['value']}'>
                            ${metric['value']} ${unit}
                        </span>
                    </p>
                `);
            });
        }
    });
}