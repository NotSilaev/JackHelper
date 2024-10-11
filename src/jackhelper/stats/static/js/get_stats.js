$(document).ready(function() {
    sendSequentialRequests();
});

function sendSequentialRequests(city, start_date, end_date) {
    stats_blocks_list = $('#stats-blocks-list');
    stats_blocks_list.empty()

    let blocks = [
        {'id': 'finance', 'title': 'Финансы'},
        {'id': 'orders', 'title': 'Заказ-наряды'},
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
    block_id = block['id']

    endpoint_url = location.href + 'api/getStatsBlock/'
    console.log(block_id)
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
            stats_blocks_list.empty()
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
                <li style="justify-content: center;">
                    ${loadingSpinner(color="#000000")}
                </li>
            </ul>
        </div>
    `
    stats_blocks_list.append(frame)
}

function addStatsBlockMetrics(response) {
    block_id = response['block_id']
    metrics = response['metrics']

    metrics_list = $('#' + block_id + ' ' + '.metrics-list')
    metrics_list.empty()

    for (const [id, metric] of Object.entries(metrics)) {
        title = metric['title']
        value = metric['value']

        frame = `
            <li id="${id}">
                <p>${title}</p>
                <h3>${value}</h3>
            </li>
        `

        metrics_list.append(frame)
    }
}
