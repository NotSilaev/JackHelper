function startSendingRequests(city, year) {
    endpoint_url = location.href + 'api/getAvailableMonths/'
    $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: {
            city: city,
            year: year,
        },

        success: function(response) {
            available_months = response['available_months'];
            sendSequentialRequests(
                selected_city, 
                selected_year, 
                available_months
            );
        },

        error: function(response) { 
            exceptionsHandler(response.responseJSON);
        }
    });
}


function sendSequentialRequests(city, year, available_months) {
    plans_list = $('#plans-list');
    plans_list.empty();

    if (available_months.length === 0) {
        plans_list.append(`
            <h3 style="font-size: 18px">Нет ни одного плана</h3>
        `)
        return;
    }

    let promise = $.Deferred().resolve();

    available_months.forEach(function(month) {
        addPlanBlockFrame(city, year, month);
    });
    available_months.forEach(function(month) {
        promise = promise.then(function() {
            return makeRequest(city, year, month);
        });
    });
}

function makeRequest(city, year, month) {
    endpoint_url = location.href + 'api/getPlanMetrics/'
    return $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: {
            city: city,
            year: year,
            month: month,
        },

        success: function(response) {
            addPlanBlockMetrics(response);
        },

        error: function(response) { 
            plans_list.empty();
            exceptionsHandler(response.responseJSON);
        }
    });
}


function addPlanBlockFrame(city, year, month) {
    plan_id = `${city}-${year}-${month}`
    
    frame = `
        <div id="${plan_id}" class="plan-block">
            <div class="plan-heading">
                <h2>${month_titles[month]}</h2>
            </div>
            <ul class="metrics-list">
                ${loadingSpinner(color="#000000")}
            </ul>
        </div>  
    `
    plans_list = $('#plans-list');
    plans_list.append(frame);
}

function addPlanBlockMetrics(response) {
    city = response['city'];
    year = response['year'];
    month = response['month'];
    metrics = response['metrics'];

    plan_id = `${city}-${year}-${month}`

    plan_heading = $(`#${plan_id} .plan-heading`);
    plan_data = `{
        'city': '${city}',
        'year': '${year}',
        'month': '${month}',
        'metrics': {
            'revenue': '${metrics[0]['plan_value']}',
            'works_revenue': '${metrics[1]['plan_value']}',
            'spare_parts_revenue': '${metrics[2]['plan_value']}',
            'normal_hours': '${metrics[3]['plan_value']}',
        }
    }`
    plan_heading.append(`
        <button onclick="showPlanWindow(${plan_data})">
            <img>
        </button>
    `)

    metrics_list = $(`#${plan_id} .metrics-list`);
    metrics_list.empty();
    metrics.forEach(function(metric){
        title = metric['title'];
        current_value = metric['current_value'];
        plan_value = metric['plan_value'];
        progress_percent = Math.trunc(current_value / plan_value * 100, 2)
        if (isNaN(progress_percent)|| progress_percent === Infinity) {
            progress_percent = 0;
        };
        metric_unit = metric['metric_unit'];

        metrics_list.append(`
            <li>
                <div class="metric-heading">
                    <h3>${title}</h3>
                    <p class="medium">${progress_percent} %</p>
                </div>
                <div class="indicators">
                    <p class="medium">${numberToContinentalStyle(current_value)} ${metric_unit}</p>
                    <hr class="dividing-line">
                    <p class="medium">${numberToContinentalStyle(plan_value)} ${metric_unit}</p>
                </div>
            </li>
        `);
    })
}
