from django.http import HttpResponse, Http404
from django.shortcuts import render
from .models import Bell, EmployeePhone, Employee, Phone, User
from .utils.minio_client import get_call_audio
from app.search_indexes import BellDocument
from elasticsearch_dsl import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Avg
from datetime import datetime
import json
from .rag_chain import run_rag_query
from .show_chroma_data import giga_query

def chat(request):
    return render(request, "chat.html")

def report(request):
    return render(request, "reports.html")

def admin_panel_data(request):
    data = []

    users = User.objects.select_related('id_employee_fk', 'id_role_fk')

    for user in users:
        employee = user.id_employee_fk
        role = user.id_role_fk.name_role if user.id_role_fk else ""

        # Находим телефон
        phone = (
            EmployeePhone.objects.filter(id_employee_fk=employee)
            .select_related('id_phone_fk')
            .first()
        )

        sip_phone = phone.id_phone_fk.sip_phone if phone and phone.id_phone_fk else ""
        external_phone = phone.id_phone_fk.external_phone if phone and phone.id_phone_fk else ""

        data.append({
            "full_name": f"{employee.surname} {employee.name} {employee.second_name or ''}",
            "login": user.login,
            "password": user.password,
            "sip_phone": sip_phone,
            "external_phone": external_phone,
            "role": role
        })

    return JsonResponse({"users": data})


def profile(request):
    return  render(request, "account.html")

def average_duration_report(request):
    operator_ids = request.GET.getlist('operator_id[]')
    date_from = request.GET.get('date_from')
    date_before = request.GET.get('date_before')

    bells = Bell.objects.all()

    if operator_ids:
        bells = bells.filter(id_employee_fk__id_employee__in=operator_ids)
    if date_from:
        bells = bells.filter(datetime_bell__date__gte=date_from)
    if date_before:
        bells = bells.filter(datetime_bell__date__lte=date_before)

    result = (
        bells.values('id_employee_fk__surname', 'id_employee_fk__name')
        .annotate(avg_duration=Avg('call_duration'))
        .order_by()
    )

    data = [
        {
            'label': f"{row['id_employee_fk__surname']} {row['id_employee_fk__name']}",
            'value': round(row['avg_duration'], 2) if row['avg_duration'] else 0
        }
        for row in result
    ]

    return JsonResponse({'data': data})

@csrf_exempt
def rag_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("query", "")
            if not query:
                return JsonResponse({"reply": "Запрос пуст."})

            reply = giga_query(query)
            return JsonResponse({"reply": reply})

        except Exception as e:
            return JsonResponse({"reply": f"Ошибка: {str(e)}"})
    return JsonResponse({"reply": "Метод не поддерживается."}, status=405)




def index(request):
    return render(request, "index.html")

def employees_list(request):

    employees = Employee.objects.all()

    return render(request, 'reports.html', {
        'employees': employees
    })

def bells_list(request):

    # Сопоставляем телефоны для сотрудников
    employee_phones = EmployeePhone.objects.select_related('id_phone_fk', 'id_employee_fk')

    employees = Employee.objects.all()

    bells = Bell.objects.select_related('id_employee_fk').order_by('-datetime_bell')

    # Фильтрация
    date_from = request.GET.get('date_from')
    date_before = request.GET.get('date_before')
    duration_from = request.GET.get('duration_from')
    duration_before = request.GET.get('duration_before')
    operator_id = request.GET.get('operator_id')
    bell_id = request.GET.get('bell_id')
    keywords = request.GET.get('keywords')
    text_search = request.GET.get('text_search')

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

    # if operator_id:
    #     bells = bells.filter(id_employee_fk__id_employee=operator_id)

    # if bell_id:
    #     bells = bells.filter(id_bell=bell_id)

    if keywords:
        for word in keywords.split():
            bells = bells.filter(text_transripct__icontains=word)

    # if text_search:
    #     es_query = Q("multi_match", query=text_search, fields=["text_transcripct"], fuzziness="auto")
    #     search_results = BellDocument.search().query(es_query).execute()
    #
    #     # Получаем все ID из Elasticsearch
    #     es_ids = [int(hit.meta.id) for hit in search_results]
    #
    #     # Выводим результаты
    #     print("=" * 50)
    #     print("РЕЗУЛЬТАТЫ ПОИСКА В ELASTICSEARCH")
    #     print(f"Поисковый запрос: '{text_search}'")
    #     print(f"Найдено результатов: {len(es_ids)}")
    #     print("Найденные ID:", es_ids)
    #     print("=" * 50)
    #
    #     bells = bells.filter(id_bell__in=es_ids)

    if text_search:
        es_query = Q("multi_match", query=text_search, fields=["text_transcript"], fuzziness="auto")
        search_results = BellDocument.search().query(es_query).execute()
        es_ids = [int(hit.meta.id) for hit in search_results]  # Привести к int если id_bell это IntegerField
        bells = bells.filter(id_bell__in=es_ids)

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
