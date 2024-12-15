import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from .models import Robot


# Отключаем проверку CSRF для упрощения (можно включить позже)
@csrf_exempt
def add_robot(request):
    if request.method == 'POST':
        try:
            # Получаем данные из тела запроса
            data = json.loads(request.body)
            model = data.get('model')
            version = data.get('version')
            created = data.get('created')

            # Валидация модели
            valid_models = ['R2', '13', 'X5']  # Список допустимых моделей
            if model not in valid_models:
                return JsonResponse({"error": f"Недопустимая модель: {model}"},
                                    status=400,
                                    json_dumps_params={'ensure_ascii': False})

            # Валидация версии
            valid_versions = ['D2', 'XS', 'LT']  # Список допустимых версий
            if version not in valid_versions:
                return JsonResponse({"error": f"Недопустимая версия: {version}"},
                                    status=400,
                                    json_dumps_params={'ensure_ascii': False})

            # Валидация даты
            created_datetime = parse_datetime(created)
            if not created_datetime:
                return JsonResponse({"error": "Некорректный формат даты. Используйте YYYY-MM-DD HH:MM:SS"},
                                    status=400,
                                    json_dumps_params={'ensure_ascii': False})

            # Генерация серийного номера
            serial = f"{model}-{version}-{created_datetime.strftime('%Y%m%d%H%M%S')}"

            # Сохранение записи в базе данных
            Robot.objects.create(serial=serial, model=model, version=version, created=created_datetime)

            return JsonResponse(
                {"message": "Робот успешно добавлен", "serial": serial},
                status=201,
                json_dumps_params={'ensure_ascii': False}  # Отключаем ASCII-кодирование
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный формат JSON"},
                                status=400,
                                json_dumps_params={'ensure_ascii': False})

    return JsonResponse({"error": "Метод не поддерживается. Используйте POST"},
                        status=405,
                        json_dumps_params={'ensure_ascii': False})
