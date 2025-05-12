from django.http import HttpResponse, Http404
from django.shortcuts import render
from .models import Bell
from .models import EmployeePhone
from .models import Employee
from .utils.minio_client import get_call_audio


def index(request):
    return render(request, "index.html")

def bells_list(request):

    # Сопоставляем телефоны для сотрудников
    employee_phones = EmployeePhone.objects.select_related('id_phone_fk', 'id_employee_fk')

    employees = Employee.objects.all();

    bells = Bell.objects.select_related('id_employee_fk').order_by('-datetime_bell')

    # Фильтрация
    date_from = request.GET.get('date_from')
    date_before = request.GET.get('date_before')
    duration_from = request.GET.get('duration_from')
    duration_before = request.GET.get('duration_before')
    operator_id = request.GET.get('operator_id')
    bell_id = request.GET.get('bell_id')
    keywords = request.GET.get('keywords')

    if date_from:
        bells = bells.filter(datetime_bell__date__gte=date_from)
    if date_before:
        bells = bells.filter(datetime_bell__date__lte=date_before)

    if duration_from:
        try:
            bells = bells.filter(call_duration__gte=int(duration_from))
        except ValueError:
            pass
    if duration_before:
        try:
            bells = bells.filter(call_duration__lte=int(duration_before))
        except ValueError:
            pass

    if operator_id:
        bells = bells.filter(id_employee_fk__id_employee=operator_id)

    if bell_id:
        bells = bells.filter(id_bell=bell_id)

    if keywords:
        for word in keywords.split():
            bells = bells.filter(text_transripct__icontains=word)

    # Срез только после всех фильтров
    bells = bells[:10]

    phone_map = {}
    for ep in employee_phones:
        if ep.id_employee_fk_id and ep.id_phone_fk:
            phone_map[ep.id_employee_fk_id] = ep.id_phone_fk

    return render(request, 'index.html', {
        'bells': bells,
        'phone_map': phone_map,
        'employees': employees
    })

def download_recording(request, bell_id):
    try:
        content = get_call_audio(bell_id)
        return HttpResponse(content, content_type='audio/wav')
    except Exception as e:
        print(f"❌ Ошибка при получении файла из MinIO: {e}")
        raise Http404("Файл не найден")
