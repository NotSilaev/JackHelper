$(document).ready(function() {
    sendAllDashboardBlocksRequests(period='day');
});

function sendAllDashboardBlocksRequests(period) {
    var period_day_button = $('#dashboard-period-day');
    var period_month_button = $('#dashboard-period-month');
    if (period === 'day') {
        period_month_button.removeClass('selected-period');
        period_day_button.addClass('selected-period');
    }
    else if (period === 'month') {
        period_day_button.removeClass('selected-period');
        period_month_button.addClass('selected-period');
    }

    sendPlansProgressRequests(period);
};