function sendNewPlanData(city, year, month) {
    revenue = $('#revenue').val()
    works_revenue = $('#works_revenue').val()
    spare_parts_revenue = $('#spare_parts_revenue').val()
    normal_hours = $('#normal_hours').val()

    if (!(city && year && month) || !(revenue && works_revenue && spare_parts_revenue && normal_hours)) {
        return showModalWindow(
            windowID='standartModal', 
            height='250px', 
            heading='Заполните все поля', 
            content=`
                Для добавления нового плана выберите город, год и месяц, а также
                заполните поля: "Выручка", "Выручка с работ", "Выручка с з/ч", "Нормо-часы". 
            `, 
            accept_text='Понял', 
            accept_action='showPlanWindow()',
        )
    }

    endpoint_url = 'api/setMonthPlan/'
    csrf_token = getCookie('csrftoken')
    $.ajax({
        url: endpoint_url,
        method: 'POST',
        data: {
            csrfmiddlewaretoken: csrf_token,
            city: city,
            year: year,
            month: month,
            revenue: revenue,
            works_revenue: works_revenue,
            spare_parts_revenue: spare_parts_revenue,
            normal_hours: normal_hours,
        },
        
        success: function(response, textStatus, jqXHR) {
            city = response['city'];
            year = response['year'];
            month = response['month'];

            if (jqXHR.status === 200) {
                showModalWindow(
                    windowID='standartModal', 
                    height='200px', 
                    heading='План изменён', 
                    content=`
                        План (${city_titles[city]} ${year} ${month_titles[month]}) был изменён.
                    `, 
                    accept_text='Понял', 
                    accept_action='null',
                )
            }
            else if (jqXHR.status === 201) {
                showModalWindow(
                    windowID='standartModal', 
                    height='200px', 
                    heading='План добавлен', 
                    content=`План (${city_titles[city]} ${year} ${month_titles[month]}) был добавлен.`, 
                    accept_text='Понял', 
                    accept_action='null',
                )
            }
            startSendingRequests(city, year)
        },

        error: function(response) { 
            exceptionsHandler(response.responseJSON);
        }
    })
}