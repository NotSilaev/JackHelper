function setPeriodTemplate(template) {
    /**
     * Sets the dates in the statistics sampling period depending on the template.
     * @param  {[String]} template [template id]
     */

    const template_days = {
        'today': 0,
        'yesterday': 1,
        'week': 7,
        'month': 30,
        'year': 365,
    };

    let currentDate = new Date();
    let end_date = formatDate(currentDate);

    let start_date;

    if (template === 'all_time') {
        start_date = '2017-01-01';
    } else {
        let daysToSubtract = template_days[template] || 0;
        let startDate = new Date();
        startDate.setDate(currentDate.getDate() - daysToSubtract);
        start_date = formatDate(startDate);
    }

    $('#start-date').val(start_date)
    $('#end-date').val(end_date).trigger('change')
}

function formatDate(date) {
    /**
     * Change date type from javascript Date to String.
     * @param  {[Date]} date [current date]
     */

    let year = date.getFullYear();
    let month = (date.getMonth() + 1).toString().padStart(2, '0');
    let day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}
