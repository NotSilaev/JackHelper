var city = 'VLG';
var date = new Date();
var year = date.getFullYear();
var month = date.getMonth() + 1;

$(document).ready(function () {
    setDefaultFiltersValues();
    sendSequentialRequests(city, year, month);
});

function setDefaultFiltersValues() {
    /* Sets default values for filters. */

    let city_filter = $('#city');
    const cities = ['VLG', 'VLZ'];
    cities.forEach(city_code => {
        if (city_code === city) {
            city_filter.append(`<option value="${city_code}" selected>${city_titles[city_code]}</option>`)
        } else {
            city_filter.append(`<option value="${city_code}">${city_titles[city_code]}</option>`)
        };
    });

    let year_filter = $('#year');
    for (var y = 2024; y <= year; y++) {
        if (y === year) {
            year_filter.append(`<option value="${y}" selected>${y}</option>`)
        } else {
            year_filter.append(`<option value="${y}">${y}</option>`)
        };
    }

    let month_filter = $('#month');
    for (var m = 1; m <= 12; m++) {
        if (m === month) {
            month_filter.append(`<option value="${m}" selected>${month_titles[m]}</option>`)
        } else {
            month_filter.append(`<option value="${m}">${month_titles[m]}</option>`)
        };
    }
};

function setSelectedFilter(filter, value) {
    /**
     * Sets the value for a specific filter.
     * @param  {[String]} filter [filter HTML element id]
     * @param  {[String]} value
     */

    if (filter === 'city') {city = value}
    else if (filter === 'year') {year = value}
    else if (filter === 'month') {month = value};

    sendSequentialRequests(city, year, month);
};

function sendSequentialRequests(city, year, month) {
    /**
     * Sends sequential requests to the backend.
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} year
     * @param  {[String]} month
     */

    const salaries_blocks_list = $('.salaries-blocks-list');
    salaries_blocks_list.empty();

    let blocks = [
        {'id': 'service_consultants', 'title': 'Сервисные консультанты'},
        {'id': 'spare_parts_managers', 'title': 'Сотрудники ОЗЧ'},
        {'id': 'mechanics', 'title': 'Механики'},
        {'id': 'directors', 'title': 'Директора'},
    ];
    let promise = $.Deferred().resolve();

    blocks.forEach(function(block) {
        addSalariesBlockFrame(block);
    });
    blocks.forEach(function(block) {
        promise = promise.then(function() {
            return makeRequest(block, city, year, month);
        });
    });
};

function makeRequest(block, city, year, month) {
    /**
     * Makes a single request to the backend.
     * @param  {[String]} block [salaries block id (example: "service_consultants")]
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} year
     * @param  {[String]} month
     */

    endpoint_url = location.href + 'api/getSalariesBlock/'
    $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: {
            block_id: block['id'],
            city: city,
            year: year,
            month: month,
        },

        success: function(response) {
            addSalariesBlock(response, city, year, month);
        },

        error: function(response) {
            exceptionsHandler(response.responseJSON);
        }
    });
};

function addSalariesBlockFrame(block) {
    /**
     * Adds a temporary empty frame while waiting for a server response.
     * @param  {[String]} block [salaries block id (example: "service_consultants")]
     */

    let salaries_blocks_list = $('.salaries-blocks-list');

    let frame = `
        <div id="${block['id']}" class="salaries-block">
            <div class="salaries-block-heading">
                <h2>${block['title']}</h2>
            </div>
            <div id="salaries-data">
                ${loadingSpinner(color="#000000")}
            </div>
        </div>
    `
    salaries_blocks_list.append(frame);
};

function addSalariesBlock(response, city, year, month) {
    /**
     * Adds a frame with block data.
     * @param  {[JSON]} response [salaries block data]
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} year
     * @param  {[String]} month
     */

    const block_id = response['block_data']['id'];
    const employees = response['employees'];
    const metrics_data = response['metrics_data'];

    const block_salaries = $(`#${block_id}`)
    var block_salaries_heading = block_salaries.find('.salaries-block-heading');
    var block_salaries_data = block_salaries.find('#salaries-data');
    block_salaries_data.empty();

    if (employees.length === 0) {
        block_salaries_data.append(`
            <p class="empty-salaries-block">Нет ни одного сотрудника с зарплатой выше 0 ₽</p>    
        `);
        return;
    }

    var table_header_cells = [];
    metrics_data.forEach(metric => {
        table_header_cells.push(`<div class="table-cell">${metric['title']}</div>`);
    });
    const table_header_frame = `
        <div class="table-header">
            ${table_header_cells.join('')}
        </div>
    `;

    var table_rows = [];
    employees.forEach(employee => {
        const fullname = employee['fullname'];
        const main_metrics = employee['metrics']['main'];
        const additional_metrics_json = JSON.stringify(employee['metrics']['additional']).replace(/"/g, '&quot;');

        let employee_row_cells = [];
        employee_row_cells.push(`<div class="table-cell">${fullname}</div>`);
        main_metrics.forEach(metric => {
            employee_row_cells.push(`
                <div class="table-cell">${numberToContinentalStyle(metric['value'])} ₽</div>
            `);
        });

        const employee_row_frame = `
            <div onclick="showEmployeeAdditionalSalaryMetricsWindow(
                    '${fullname}', 
                    ${additional_metrics_json},
                    '${city}',
                    ${year},
                    ${month},
                 );" 
                 class="table-row clickable-row">
                ${employee_row_cells.join('')}
            </div>`;
        table_rows.push(employee_row_frame);
    });
    const table_rows_frame = table_rows.join('');

    const block_data = JSON.stringify(response).replace(/"/g, '&quot;');
    const block_salaries_details_button_frame = `                
        <button onclick="showSalariesBlockDetailsWindow(${block_data});">
            <img class="salary-block-details-icon">
        </button>
    `;
    const block_salaries_data_frame = `
        <div id="salaries-data">
        <div class="table-container">
            <div class="table">
                ${table_header_frame}
                ${table_rows_frame}
            </div>
        </div>
    `;

    block_salaries_heading.append(block_salaries_details_button_frame);
    block_salaries_data.append(block_salaries_data_frame);
};