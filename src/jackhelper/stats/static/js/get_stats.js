$(document).ready(function() {
    sendSequentialRequests();
});

function sendSequentialRequests(city, start_date, end_date) {
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
            stats_blocks_list.empty();
            exceptionsHandler(response.responseJSON);
        }
    });
}


function addStatsBlockFrame(block) {
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
        metric_submetrics_unit = metric['submetrics_unit'];

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

                if (typeof submetric_value === 'number') {
                    submetric_value = numberToContinentalStyle(submetric_value);
                }
                if (submetric_value !== null) {
                    if (metric_submetrics_unit !== undefined) {
                        submetric_value = `${submetric_value} ${metric_submetrics_unit}`;
                    } 
                    else if (metric_unit !== undefined) {
                        submetric_value = `${submetric_value} ${metric_unit}`;
                    };
                };
                if (submetric_value === null) {
                    submetric_value = 'Ошибка загрузки';
                };

                submetrics_list.append(`
                    <li>
                        <p>${submetric_title}</p>
                        <h3>${submetric_value}</h3>
                    </li>
                `)
            })
        }
    })
}
