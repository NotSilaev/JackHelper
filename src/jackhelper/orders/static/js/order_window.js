function showOrderWindow(fullnumber, metrics) {
    var window_height = 75;

    metric_frames = []
    metrics.forEach(metric => {
        unit = metric['unit'];
        if (unit === undefined) {
            unit = '';
        };
        metric_frames.push(`
            <div class="order-data-field">
                <h3>${metric['title']}</h3>
                <p class="truncate-text" title='${metric['value']}'>
                    ${metric['value']} ${unit}
                </p>
            </div>    
        `);
        window_height += 75;
    });

    order_frame = `<div class="order-data">${metric_frames.join('')}</div>`

    showModalWindow(
        windowID='standartModal', 
        height=window_height.toString(), 
        heading=`Заказ-наряд #${fullnumber}`, 
        content=order_frame,
    )
}

