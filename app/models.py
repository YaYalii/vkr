from django.db import models
from django.contrib.postgres.fields import ArrayField

class Role(models.Model):
    id_role = models.AutoField(primary_key=True)
    name_role = models.CharField(max_length=100)

    def __str__(self):
        return self.name_role


class Employee(models.Model):
    id_employee = models.AutoField(primary_key=True)
    surname = models.CharField(max_length=100)
    name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=60, null=True, blank=True)

    def __str__(self):
        return f"{self.surname} {self.name}"


class Phone(models.Model):
    id_phones = models.AutoField(primary_key=True)
    sip_phone = models.CharField(max_length=30)
    external_phone = models.CharField(max_length=30)

    def __str__(self):
        return str(self.external_phone)


class EmployeePhone(models.Model):
    id_employee_phone = models.AutoField(primary_key=True)
    id_employee_fk = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    id_phone_fk = models.ForeignKey(Phone, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.id_employee_fk} - {self.id_phone_fk}"


class User(models.Model):
    id_user = models.AutoField(primary_key=True)
    id_role_fk = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    id_employee_fk = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    login = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

    def __str__(self):
        return str(self.login)


class Bell(models.Model):
    id_bell = models.AutoField(primary_key=True)
    id_employee_fk = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    call_reccording = models.CharField(max_length=200)
    datetime_bell = models.DateTimeField()
    client_phone = models.CharField(max_length=20)
    call_duration = models.IntegerField()
    text_transripct = models.TextField(null=True, blank=True)
    # vector = models.TextField(null=True, blank=True)
    keyword = models.TextField(null=True, blank=True)
    embedding = ArrayField(models.FloatField(), null=True, blank=True)

    def __str__(self):
        return f"Call {self.id_bell} at {self.datetime_bell}"

