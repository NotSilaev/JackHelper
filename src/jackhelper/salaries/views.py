from django.template.response import TemplateResponse
from django.http import FileResponse

import os


def salaries(request):
    return TemplateResponse(request, 'salaries/salaries.html')

def downloadSalariesFile(request, filename):
    file_path = os.path.join('salaries/salaries_xlsx_files', filename)

    if os.path.exists(file_path) is False:
        raise ValueError('File not found')

    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response