function showPlanWindow(plan_data=null) {
    if (plan_data !== null) {
        city = plan_data['city'];
        year = plan_data['year'];
        month = plan_data['month'];

        metrics = plan_data['metrics'];
        revenue = metrics['revenue'];
        works_revenue = metrics['works_revenue'];
        spare_parts_revenue = metrics['spare_parts_revenue'];

        plan_frame = `
            <div class="plan-window">
                <div class="plan-data horizontal">
                    <h3>${city_titles[city]}</h3>
                    <hr class="dividing-line">
                    <h3>${year}</h3>
                    <hr class="dividing-line">
                    <h3>${month_titles[month]}</h3>
                </div>
                <div class="plan-data">
                    <input id="revenue" value="${revenue}" placeholder="Выручка">
                    <input id="works_revenue" value="${works_revenue}" placeholder="Выручка с работ">
                    <input id="spare_parts_revenue" value="${spare_parts_revenue}" placeholder="Выручка с з/ч">
                </div>
            </div>
        `
        
        window_height = '300px';
        window_heading = 'Редактирование плана';
        window_accept_text = 'Сохранить';
        window_accept_action = `
            sendNewPlanData(
                city="${city}",
                year=${year},
                month=${month},
            )
        `
    } 
    else {
        var city = undefined;
        var year = undefined;
        var month = undefined;
        function setParameterValue(param, value) {
            if (param === 'city') {
                selected_city = value;
            }
            else if (param === 'year') {
                selected_year = value;
            }
            else if (param === 'month') {
                selected_month = value;
            }
        }

        plan_frame = `
            <div class="plan-window">
                <div class="plan-data">
                    <select id="parameter-city">
                        <option selected disabled>Город</option>
                        <option value="VLG">Волгоград</option>
                        <option value="VLZ">Волжский</option>
                    </select>
                    <select id="parameter-year">
                        <option selected disabled>Год</option>
                        <option value="2024">2024</option>
                        <option value="2025">2025</option>
                    </select>
                    <select id="parameter-month">
                        <option selected disabled>Месяц</option>
                        <option value="1">Январь</option>
                        <option value="2">Февраль</option>
                        <option value="3">Март</option>
                        <option value="4">Апрель</option>
                        <option value="5">Май</option>
                        <option value="6">Июнь</option>
                        <option value="7">Июль</option>
                        <option value="8">Августь</option>
                        <option value="9">Сентябрь</option>
                        <option value="10">Октябрь</option>
                        <option value="11">Ноябрь</option>
                        <option value="12">Декабрь</option>
                    </select>
                </div>
                <div class="plan-data">
                    <input id="revenue" placeholder="Выручка">
                    <input id="works_revenue" placeholder="Выручка с работ">
                    <input id="spare_parts_revenue" placeholder="Выручка с з/ч">
                </div>
            </div>
        `

        window_height = '420px';
        window_heading = 'Добавление плана';
        window_accept_text = 'Добавить';
        window_accept_action = `
            sendNewPlanData(
                city=$('#parameter-city').val(),
                year=$('#parameter-year').val(),
                month=$('#parameter-month').val(),
            )
        `
    }

    showModalWindow(
        windowID='standartModal', 
        height=window_height, 
        heading=window_heading, 
        content=plan_frame, 
        accept_text=window_accept_text, 
        accept_action=window_accept_action,
    )
}