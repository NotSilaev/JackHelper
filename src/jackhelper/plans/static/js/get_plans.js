function startSendingRequests(city, year) {
    /**
     * Starts sending sequential requests to the backend.
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} year [plan year]
     */

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

            addPlanBlockFrame(city, year);
            getAnnualPlan(
                selected_city,
                selected_year
            )
        },

        error: function(response) { 
            exceptionsHandler(response.responseJSON);
        }
    });
}


function sendSequentialRequests(city, year, available_months) {
    /**
     * Sends sequential requests to the backend.
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} year [plan year]
     * @param  {[Array]} available_months [list of available plan months]
     * @return {[function]} makeRequest [makes single request]
     */

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
            return getMonthlyPlan(city, year, month);
        });
    });
}

function getMonthlyPlan(city, year, month) {
    /**
     * Gets a monthly plan from the backend.
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} year [plan year]
     * @param  {[String]} month [plan month]
     */

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

function getAnnualPlan(city, year) {
    /**
     * Gets an annual plan from the backend.
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} year [plan year]
     */

    endpoint_url = location.href + 'api/getAnnualPlanMetrics/'
    return $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: {
            city: city,
            year: year,
        },

        success: function(response) {
            const plan_data = {
                'city': response['city'],
                'year': response['year'],
                'metrics': Object.values(response['plan']['metrics']),
            };
            addPlanBlockMetrics(plan_data);
        },

        error: function(response) { 
            plans_list.empty();
            exceptionsHandler(response.responseJSON);
        }
    });
}

function addPlanBlockFrame(city, year, month) {
    /**
     * Adds a temporary empty frame while waiting for a server response.
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} year [plan year]
     * @param  {[String || undefined]} month [plan month]
     */

    if (month) {
        var plan_id = `${city}-${year}-${month}`;
        var plan_title = month_titles[month];

        const date = new Date();
        var current_month = date.getMonth() + 1;
        if (current_month <= 6) {var order = month} else {var order = 12-month};
        if (month === current_month) {
            var order = -1;
        }

    } else {
        var plan_title = `${year} год`;
        var plan_id = `${city}-${year}`;
        var order = -2; // Plan without month is annual plan and its on the first place
    }
    
    frame = `
        <div id="${plan_id}" class="plan-block" style="order: ${order}">
            <div class="plan-heading">
                <h2>${plan_title}</h2>
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
    /**
     * Adds a frame with plan data.
     * @param  {[JSON]} response [plan data]
     */

    var city = response['city'];
    var year = response['year'];
    var month = response['month'];
    var metrics = response['metrics'];

    if (month) {
        var plan_is_annual = false;
        var plan_id = `${city}-${year}-${month}`;
    } else {
        var plan_id = `${city}-${year}`;
        var plan_is_annual = true;
    };

    if (metrics.length === 0) {
        $(`#${plan_id}`).remove();
    }

    plan_heading = $(`#${plan_id} .plan-heading`);
    if (plan_is_annual === false) {
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
    };

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
