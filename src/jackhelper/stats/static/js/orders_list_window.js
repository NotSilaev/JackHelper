function showOrdersByPercentWindow(percent, orders) {
    /**
     * Сreates a modal window with a list of orders.
     * @param  {[Number]} percent [the common orders discount percent]
     * @param  {[Array]} orders [orders list]
     */

    order_frames = [];

    orders.forEach(order => {
        order_frame = `
            <li>
                <h3>
                    #${order['fullnumber']}
                    <span>${order['date']}</span>
                </h3>
                <p>${order['metrics'][0]['value']}</p>
            </li>
        `
        order_frames.push(order_frame);
    });

    order_frame = `
        <ul class="orders-by-percent-list">
            ${order_frames.join('')}
        </ul>
    `

    showModalWindow(
        windowID='standartModal', 
        height='500px', 
        heading=`ЗН со скидкой ${percent}%`, 
        content=order_frame,
    )
}


function getOrdersByPercent(percent, city, start_date, end_date) {
    /**
     * Obtains orders by one discount percent.
     * @param  {[Number]} percent [the common orders discount percent]
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} start_date [period start date]
     * @param  {[String]} end_date [period end date]
     */

    with (location) {
        if (['localhost', '127.0.0.1'].includes(hostname)) {
            href_root = protocol + '//' + hostname + ':' + port
        } else {
            href_root = protocol + '//' + hostname
        }
    }
    endpoint_url = href_root + '/orders/api/getOrders/'
    return $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: {
            city: city,
            start_date: start_date,
            end_date: end_date,
            tags: JSON.stringify(['with_discount_gte_11']),
            page: 0,
        },

        success: function(response) {
            orders = response['orders']['list']
            orders_with_current_percent = []

            orders.forEach(order => {
                discount_percent = order['metrics'][1]['value']
                if (discount_percent === percent) {
                    orders_with_current_percent.push(order)
                }
            });

            showOrdersByPercentWindow(percent, orders_with_current_percent)
        },

        error: function(response) {
            exceptionsHandler(response.responseJSON);
        }
    });
}