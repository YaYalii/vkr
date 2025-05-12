# Импорт модуля admin из библиотеки Django.contrib
from django.contrib import admin
# Импорт модели MyModel из текущего каталога (".")
from .models import Role
from .models import User
from .models import Bell
from .models import Employee
from .models import EmployeePhone
from .models import Phone

# Регистрация модели MyModel для административного сайта
admin.site.register(Role)
admin.site.register(User)
admin.site.register(Bell)
admin.site.register(Employee)
admin.site.register(EmployeePhone)
admin.site.register(Phone)
