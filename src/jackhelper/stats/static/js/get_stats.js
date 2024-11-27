$(document).ready(function() {
    sendSequentialRequests();
});

function sendSequentialRequests(city, start_date, end_date) {
    /**
     * Sends sequential requests to the backend.
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} start_date [period start date]
     * @param  {[String]} end_date [period end date]
     * @return {[function]} makeRequest [makes single request]
     */

    stats_blocks_list = $('#stats-blocks-list');
    stats_blocks_list.empty();

    let blocks = [
        {'id': 'finance', 'title': 'Финансы'},
        {'id': 'orders', 'title': 'Заказ-наряды'},
        {'id': 'normal_hours', 'title': 'Нормо-часы'},
        {'id': 'diagnostic_packages', 'title': 'Пакеты диагностик при ТО'},
    ];
    let promise = $.Deferred().resolve();

    blocks.forEach(function(block) {
        addStatsBlockFrame(block);
    });
    blocks.forEach(function(block) {
        promise = promise.then(function() {
            return makeRequest(block, city, start_date, end_date);
        });
    });
}

function makeRequest(
    block,
    city,
    start_date,
    end_date
) {
    /**
     * Makes a single request to the backend.
     * @param  {[String]} block [statistic block id (example: "finance")]
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} start_date [period start date]
     * @param  {[String]} end_date [period end date]
     */

    block_id = block['id'];

    endpoint_url = location.href + 'api/getStatsBlock/'
    return $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: {
            block_id: block_id,
            city: city,
            start_date: start_date,
            end_date: end_date,
        },

        success: function(response) {
            addStatsBlockMetrics(response);
        },

        error: function(response) {
            exceptionsHandler(response.responseJSON);
        }
    });
}


function addStatsBlockFrame(block) {
    /**
     * Adds a temporary empty frame while waiting for a server response.
     * @param  {[String]} block [statistics block id (example: "finance")]
     */

    stats_blocks_list = $('#stats-blocks-list');
    
    frame = `
        <div id=${block['id']} class="stats-block">
            <div class="heading">
                <h2>${block['title']}</h2>
            </div>
            <ul class="metrics-list">
                <li>
                    <div class="metric-data" style="justify-content: center;">
                        ${loadingSpinner(color="#000000")}
                    </div>
                </li>
            </ul>
        </div>
    `
    stats_blocks_list.append(frame);
}

function addStatsBlockMetrics(response) {
    /**
     * Adds a frame with block data.
     * @param  {[JSON]} response [stastics block data]
     */

    block_id = response['block_id'];
    metrics = response['metrics'];

    metrics_list = $('#' + block_id + ' ' + '.metrics-list');
    metrics_list.empty();

    metrics.forEach(function(metric){
        metric_id = metric['id'];
        metric_title = metric['title'];
        metric_value = metric['value'];
        metric_unit = metric['unit'];
        metric_submetrics = metric['submetrics'];

        if (typeof metric_value === 'number') {
            metric_value = numberToContinentalStyle(metric_value);
        }
        if (metric_value !== null && metric_unit !== undefined) {
            metric_value = `${metric_value} ${metric_unit}`;
        };
        if (metric_value === null) {
            metric_value = 'Ошибка загрузки';
        };

        metrics_list.append(`
            <li id="${metric_id}">
                <div class="metric-data">
                    <p>${metric_title}</p>
                    <h3>${metric_value}</h3>
                </div>
            </li>
        `);

        if (metric_submetrics) {
            metric_frame = metrics_list.find('#' + metric_id)
            metric_frame.find('.metric-data').css('border-radius', '15px 15px 0 0');
            metric_frame.append('<ul class="submetrics-list"></ul>')
            submetrics_list = metric_frame.find('.submetrics-list')

            metric_submetrics.forEach(function(submetric) {
                submetric_title = submetric['title']
                submetric_value = submetric['value']
                submetric_unit = submetric['unit']
                submetric_action = submetric['on_click_javascript_action']

                if (typeof submetric_value === 'number') {
                    submetric_value = numberToContinentalStyle(submetric_value);
                }
                if (submetric_value !== undefined) {
                    if (submetric_unit !== undefined) {
                        submetric_value = `${submetric_value} ${submetric_unit}`;
                    } else {
                        submetric_value = `${submetric_value}`
                    }
                } else {
                    submetric_value = 'Ошибка загрузки';
                };

                if (submetric_action) {
                    submetric_block_startswith = `
                        <li class="clickable-submetric" onclick="${submetric_action}">
                    `
                } else {
                    submetric_block_startswith = '<li>'
                }

                submetric_block = (
                    submetric_block_startswith + `
                        <p>${submetric_title}</p>
                        <h3>${submetric_value}</h3>
                    </li>
                `
                )
                submetrics_list.append(`${submetric_block}`)
            })
        }
    })
}
