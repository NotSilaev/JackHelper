function showEmployeeAdditionalSalaryMetricsWindow(
    fullname, 
    additional_metrics,
    city,
    year,
    month
) {
    /**
     * Сreates a modal window with a list of employee additional salary metrics.]
     * @param  {[String]} fullname [employee fullname]
     * @param  {[Array]} additional_metrics
     * @param  {[String]} city [employee city]
     * @param  {[Number]} year [salary year]
     * @param  {[Number]} month [salary month]
     */

    const allTypes = ['bonus', 'deducation'];
    const metrics_amounts = additional_metrics.reduce((acc, obj) => {
        if (!acc[obj.type]) {
            acc[obj.type] = 0;
        }
        acc[obj.type] += obj.value;
        return acc;
    }, {});
    allTypes.forEach(type => {
        if (!metrics_amounts[type]) {
            metrics_amounts[type] = 0;
        }
    });

    var additional_metrics_frames = [];
    additional_metrics.forEach(metric => {
        additional_metrics_frames.push(`
            <li id="additional_metric-${metric['id']}">
                <div class="additional-metric-heading">
                    <div>
                        <img class="salary-${metric['type']}-icon">
                        <h3>${numberToContinentalStyle(metric['value'])} ₽</h3>
                    </div>
                    <button onclick="removeSalaryMetric(${metric['id']}, '${city}', ${year}, ${month});">
                        <img class="remove-salary-metric-icon">
                    </button>
                </div>
                <p>${metric['comment']}</p>
            </li>    
        `);
    });
    if (additional_metrics_frames.length > 0) {
        var additional_metrics_list_frame = `
        <div class="employee-additional-salary-metrics">
            <ul class="additional-metrics-amount">
                <li>
                    <img class="salary-bonus-icon">
                    <p>${numberToContinentalStyle(metrics_amounts['bonus'])} ₽</p>
                </li>
                <li>
                    <img class="salary-deducation-icon">
                    <p>${numberToContinentalStyle(metrics_amounts['deducation'])} ₽</p>
                </li>
            </ul>
            <ul class="employee-additional-salary-metrics-list">
                ${additional_metrics_frames.join('')}
            </ul>
        </div>
    `;
        var modal_window_height = '500px';
    } else {
        var additional_metrics_list_frame = 'У сотрудника нет ни одного бонуса или вычета';
        var modal_window_height = '220px';
    };


    showModalWindow(
        windowID='standartModal', 
        height=modal_window_height, 
        heading=`${fullnameToInitials(fullname)} (бонусы и вычеты)`, 
        content=additional_metrics_list_frame,
        accept_text="Добавить бонус/вычет",
        accept_action=`
            showAddEmployeeSalaryMetricWindow(
                '${fullname}', '${city}', ${year}, ${month}
            );
        `,
    );
};


function showAddEmployeeSalaryMetricWindow(fullname, city, year, month) {
    const add_salary_metric_frame = `
        <div class="add-salary-metric">
            <div>
                <h3>Сотрудник</h3>
                <p>${fullnameToInitials(fullname)}</p>
            </div>
            <div>
                <h3>Сумма</h3>
                <input id="metric-amount" type="text" placeholder="Введите сумму">
            </div>
            <textarea id="metric-comment" placeholder="Введите комментарий"></textarea>
            <ul class="select-metric-type">
                <li>
                    <input type="radio" id="bonus" name="metric-type" checked="checked">
                    <label for="bonus">Бонус</label>
                </li>
                <li>
                    <input type="radio" id="deducation" name="metric-type">
                    <label for="deducation">Вычет</label>
                </li>
            </ul>
        </div>
    `

    showModalWindow(
        windowID='standartModal', 
        height='370px', 
        heading=`Добавить бонус/вычет`, 
        content=add_salary_metric_frame,
        accept_text='Добавить',
        accept_action=`addNewSalaryMetric('${fullname}', '${city}', '${year}', '${month}')`
    );  
};