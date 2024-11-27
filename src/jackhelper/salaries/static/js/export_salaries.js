function exportSalariesToExcel(city, year, month) {
    showModalWindow(
        windowID='standartModal', 
        height='235px', 
        heading='Экспорт данных', 
        content=`
            <div class="export-window-content">
                <loader>${loadingSpinner(color="#000000")}</loader>
                <p>Выгружаем зарплаты в файл.<br>Не закрывайте текущую страницу.</p>
            </div>
        `, 
        accept_text=null, 
        accept_action=null,
    );

    const endpoint_url = 'api/getSalariesExcelFileDownloadURL/';
    $.ajax({
        url: endpoint_url,
        method: 'GET',
        data: {
            city: city,
            year: year,
            month: month,
        },

        success: function(response) {
            const download_url = response['download_url'];
            showModalWindow(
                windowID='standartModal', 
                height='235px', 
                heading='Файл готов', 
                content=`
                    <div class="export-window-content">
                        <p>Файл с зарплатами успешно сформирован</p>
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