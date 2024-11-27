function showSalariesBlockDetailsWindow(block_data) {
    const employees = block_data['employees'];
    const metrics_data = block_data['metrics_data'];

    let employees_salaries_details_frames = [];
    employees.forEach(employee => {
        const fullname = employee['fullname'];
        const main_metrics = employee['metrics']['main'];

        let metrics_details_strings = [];
        let metrics_details_frames = [];

        main_metrics
            .filter(metric => 'details' in metric)
            .forEach(metric => {
                const title = metrics_data.find(item => item.id === metric['id'])?.title || null;

                if (metric['details'].length > 0) {
                    let metric_details_strings_list = [];
                    let metric_details_frames_list = [];
                    metric['details'].forEach((detail, detail_index) => {
                        const description = detail['description'];
                        const amount = detail['amount'];
                        const detail_string = (
                            `${detail_index+1}. ${description} — ${numberToContinentalStyle(amount)} ₽`
                        );
                        metric_details_strings_list.push(detail_string);
                        metric_details_frames_list.push(`
                            <li class="metric-detail">
                                <p>${description}</p>
                                <p class="important-data">${numberToContinentalStyle(amount)} ₽</p>
                            </li>
                        `);
                    });
                    var metric_details_strings = metric_details_strings_list.join('\n');
                    var metric_details_frames = metric_details_frames_list.join('\n');
                } else {
                    var metric_details_strings = 'Нет данных.';
                    var metric_details_frames = '<p class="empty-metric-details">Нет данных.</p>';
                };

                const metric_details_string = `===== ${title} =====\n${metric_details_strings}\n\n`
                const metric_details_frame = `
                    <div class="metric-details">
                        <h3>${title}</h3>
                        <ul class="metric-details-list">
                            ${metric_details_frames}
                        </ul>
                    </div>
                `
                metrics_details_strings.push(metric_details_string);
                metrics_details_frames.push(metric_details_frame);
        });

        const text_for_copy = `${fullname}\n\n${metrics_details_strings.join('')}`.replace(/"/g, '&quot;');
        const employee_metrics_details_frame = `${metrics_details_frames.join('')}`
        const employee_salaries_details_frame = `
            <div class="employee-salaries-details">
                <div class="employee-salaries-details-heading">
                    <h3>${fullnameToInitials(fullname)}</h3>
                    <button onclick="navigator.clipboard.writeText(\`${text_for_copy}\`);">
                        <img class="copy-icon">
                    </button>
                </div>
                <div class="employee-salaries-details-metrics">
                    ${employee_metrics_details_frame}
                </div>
            </div>
        `;
        employees_salaries_details_frames.push(
            employee_salaries_details_frame
        );
    });

    const salaries_block_details_frame = `
        <div class="salaries-block-details">
            ${employees_salaries_details_frames.join('')}
        </div>
    `;
    showModalWindow(
        windowID='standartModal', 
        height='500px', 
        heading=`Расшифровка зарплат`, 
        content=salaries_block_details_frame,
        accept_text=null,
        accept_action=null,
    );
};