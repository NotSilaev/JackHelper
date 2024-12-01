function sendPlansProgressRequests(period_code) {
    /** 
     * Sends sequential requests to the backend.
     * @param  {[String]} period_code [the code indicating the date range]
     */

    const cities = ['VLG', 'VLZ'];
    const date = new Date();
    let year = date.getFullYear();
    let month = date.getMonth() + 1;

    plans_progress_list = $('.plans-progress-list');
    plans_progress_list.empty();

    cities.forEach(city_code => {
        addPlanProgressFrame(city_code);
    });

    let promise = $.Deferred().resolve();
    cities.forEach((city_code, city_index) => {
        const city = {
            'code': city_code,
            'index': city_index,
        };
        promise = promise.then(function() {
            makeRequest(city, year, month, period_code);
        });
    });
}


function makeRequest(city_data, year, month, period_code) {
    /** 
     * Makes a single request to the backend.
     * @param  {[String]} city_data [contais city code and index in array]
     * @param  {[String]} year [plan year]
     * @param  {[String]} month [plan month]
     * @param  {[String]} period_code [the code indicating the date range]
     */

    with (location) {
        if (['localhost', '127.0.0.1'].includes(hostname)) {
            href_root = protocol + '//' + hostname + ':' + port
        } else {
            href_root = protocol + '//' + hostname
        }
    }
    endpoint_url = href_root + '/plans/api/getPlanMetrics/'
    return $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: {
            city: city_data['code'],
            year: year,
            month: month,
        },

        success: function(response) {
            addPlanProgressBlock(city_data, response, period_code);
        },

        error: function(response) {
            exceptionsHandler(response.responseJSON);
        }
    });
}


function addPlanProgressFrame(city_code) {
    /**
     * Adds a frame with plan progress data.
     * @param  {[String]} city_code [city code (example: "VLG")]
     * @param  {[Number]} city_index [city index number in the sequ]
     */   

    const plan_progress_frame = `
        <div id="plan_progress-${city_code}" class="plan-progress">
            <h3>
                ${city_titles[city_code]}
            </h3>
            <div class="plan-metrics-progress">
                ${loadingSpinner(color="#000000")}
            </div>
        </div>
    `;

    var plans_progress_list = $('.plans-progress-list');
    plans_progress_list.append(plan_progress_frame);
};


function addPlanProgressBlock(city_data, response, period_code) {
    /**
     * Adds a frame with plan progress data.
     * @param  {[String]} city_data [contais city code and index in array]
     * @param  {[JSON]} response [stastics block data]
     * @param  {[String]} period_code [the code indicating the date range]
     */

    var plans_progress_list = $('.plans-progress-list');
    plans_progress_list.find(`#plan_progress-${city_data['code']}`).remove()

    const city = city_data['code'];
    const year = response['year'];
    const month = response['month'];
    const metrics = response['metrics'];

    const date = new Date();
    var day = date.getDate();
    let days_in_month = getDaysInMonth(year, month);
    const hours = date.getHours();

    const autodealer_db_update_hour = 21;
    if (hours < autodealer_db_update_hour) {
        date.setDate(day - 1);
        var day = date.getDate();
    }

    var metrics_percents = [];

    function fetchCurrentValue(metric_id) {
        /**
         * Retrieves the current metric value from the backend.
         * @param  {[String]} metric_id
         */

        const blockMapping = {
            'revenue': 'finance',
            'works_revenue': 'finance',
            'spare_parts_revenue': 'finance',
            'hours_count': 'normal_hours'
        };
        
        let block_id = blockMapping[metric_id] || null;
        if (block_id === null) {
            return null;
        };

        return new Promise((resolve, reject) => {
            with (location) {
                if (['localhost', '127.0.0.1'].includes(hostname)) {
                    href_root = protocol + '//' + hostname + ':' + port
                } else {
                    href_root = protocol + '//' + hostname
                }
            }
            endpoint_url = href_root + '/stats/api/getStatsBlock/'
            $.ajax({
                url: endpoint_url,
                method: 'GET',
                data: {
                    block_id: block_id,
                    city: city,
                    start_date: `${year}-${month}-${day}`,
                    end_date: `${year}-${month}-${day}`, 
                },
        
                success: function(response) {
                    response['metrics'].forEach(metric => {
                        if (metric['id'] === metric_id) {
                            response_current_value = metric['value'];
                        };
                    });
                    resolve(response_current_value);
                },
        
                error: function(response) { 
                    plans_progress_list.empty();
                    reject(exceptionsHandler(response.responseJSON));
                }
            });
        });
    }

    (async function() {
        const metricIDs = {
            'Выручка': 'revenue',
            'Выручка с работ': 'works_revenue',
            'Выручка с з/ч': 'spare_parts_revenue',
            'Нормо-часы': 'hours_count'
        };
        
        for (let metric of metrics) {
            const metric_title = metric['title'];
            let metric_id = metricIDs[metric_title] || null;
            if (metric_id === null) {
                continue;
            };

            if (period_code === 'day') {
                var period_value = metric['plan_value'] / days_in_month;
                var current_value = await fetchCurrentValue(metric_id);
            } else if (period_code === 'month') {
                var period_value = metric['plan_value'] / days_in_month * day;
                var current_value = metric['current_value'];
            }

            let plan_percent = Math.trunc((metric['current_value'] / metric['plan_value']) * 100, 2);
            if (isNaN(plan_percent) || plan_percent === Infinity) {
                plan_percent = 0;
            }
            let period_percent = Math.trunc((current_value / period_value) * 100, 2);
            if (isNaN(period_percent) || period_percent === Infinity) {
                period_percent = 0;
            }

            metrics_percents.push({
                'title': metric_title, 
                'plan_percent': plan_percent,
                'period_percent': period_percent,
            });
        }

        var plan_metrics_frames = [];
        metrics_percents.forEach(metric => {
            const metric_title = metric['title'];
            const plan_percent = metric['plan_percent'];
            const period_percent = metric['period_percent'];
            if (period_code === 'day') {
                var displayed_percent = period_percent;
            }
            else if (period_code === 'month') {
                var displayed_percent = plan_percent;
            };
            const circle_color = period_percent < 100 ? 'c52929' : '4caf50';

            const metric_circle = getCircleFrame(
                id=`plan_${city}_${year}_${month}_${metric_title}`, 
                width=75, heigth=75, 
                percent=period_percent, 
                internal_text=`${displayed_percent}%`,
                show_internal_text=true,
                circle_color
            );
            const metric_frame = `
                <div class="metric-progress">
                    ${metric_circle}
                    ${metric_title}
                </div>
            `;
            plan_metrics_frames.push(metric_frame);
        });
        const plan_metrics_frame = plan_metrics_frames.join('');

        const plan_progress_block = `
            <div id="plan_progress-${city}_${year}_${month}" class="plan-progress" style="order: ${city_data['index']}">
                <h3>
                    ${city_titles[city]} <span>${month_titles[month]} ${year}</span>
                </h3>
                <div class="plan-metrics-progress">
                    ${plan_metrics_frame}
                </div>
            </div>
        `;
        
        plans_progress_list.append(plan_progress_block);
    })();
}