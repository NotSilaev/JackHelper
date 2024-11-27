function addNewSalaryMetric(fullname, city, year, month) {
    /**
     * Sends a request with new salary metric data to the backend.
     * @param  {[String]} fullname [employee fullname]
     * @param  {[String]} city [city code (example: "VLG")]
     * @param  {[String]} year [plan year]
     * @param  {[String]} month [plan month]
     */

    const metric_amount = $('#metric-amount').val();
    const metric_comment = $('#metric-comment').val();
    const metric_type = document.querySelector('input[name="metric-type"]:checked').id;

    if (!(metric_amount) || !(isNumeric(metric_amount))) {
        return showModalWindow(
            windowID='standartModal', 
            height='200px', 
            heading='Заполните все поля', 
            content=`Для добавления новой зарплатной метрики, введите её сумму.`, 
            accept_text='Понял', 
            accept_action='null',
        );
    };

    endpoint_url = 'api/addSalaryMetric/'
    csrf_token = getCookie('csrftoken')
    $.ajax({
        url: endpoint_url,
        method: 'POST',
        data: {
            csrfmiddlewaretoken: csrf_token,
            fullname: fullname,
            city: city,
            year: year,
            month: month,
            metric_amount: metric_amount,
            metric_comment: metric_comment,
            metric_type: metric_type,
        },
        
        success: function(response) {
            const metric_type_titles = {
                'bonus': 'Бонус',
                'deducation': 'Вычет',
            };
            const metric_type_title = metric_type_titles[metric_type];

            showModalWindow(
                windowID='standartModal', 
                height='220px', 
                heading=`${metric_type_title} добавлен`, 
                content=`
                    ${metric_type_title} в размере 
                    <span class="important-data">${numberToContinentalStyle(Number(metric_amount))}₽</span> 
                    добавлен для <span class="important-data">${fullnameToInitials(fullname)}</span> 
                `, 
                accept_text='Понял', 
                accept_action='null',
            );
            sendSequentialRequests(city, year, month);
        },

        error: function(response) { 
            exceptionsHandler(response.responseJSON);
        }
    });
};


function removeSalaryMetric(metric_id, city, year, month, accepted=false) {
    if (accepted === false) {
        return showModalWindow(
            windowID='standartModal', 
            height='200px', 
            heading='Подтвердите действие', 
            content='Вы уверены, что хотите удалить данную метрику?', 
            accept_text='Удалить', 
            accept_action=`removeSalaryMetric(${metric_id}, '${city}', ${year}, ${month}, accepted=true);`,
        );
    };

    endpoint_url = 'api/removeSalaryMetric/'
    csrf_token = getCookie('csrftoken')
    $.ajax({
        url: endpoint_url,
        method: 'POST',
        data: {
            csrfmiddlewaretoken: csrf_token,
            metric_id: metric_id,
        },
        
        success: function(response) {
            showModalWindow(
                windowID='standartModal', 
                height='200px', 
                heading='Метрика удалена', 
                content='Зарплатная метрика удалена', 
                accept_text='Понял', 
                accept_action='null',
            );
            sendSequentialRequests(city, year, month);
        },

        error: function(response) { 
            exceptionsHandler(response.responseJSON);
        }
    });
};