function exportDataToExcel(endpoint_url, data) {
    showModalWindow(
        windowID='standartModal', 
        height='235px', 
        heading='Экспорт данных', 
        content=`
            <div class="export-window-content">
                <loader>${loadingSpinner(color="#000000")}</loader>
                <p>Выгружаем данные в Excel-документ.<br>Не закрывайте текущую страницу.</p>
            </div>
        `, 
        accept_text=null, 
        accept_action=null,
    );

    $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: data,

        success: function(response) {
            const download_url = response['download_url'];
            showModalWindow(
                windowID='standartModal', 
                height='235px', 
                heading='Документ готов', 
                content=`
                    <div class="export-window-content">
                        <p>Excel-документ успешно сформирован</p>
                        <a href="${download_url}" download>Скачать</a>
                    </div>
                `, 
                accept_text=null, 
                accept_action=null,
            );
        },

        error: function(response) {
            exceptionsHandler(response.responseJSON);
        }
    });
};