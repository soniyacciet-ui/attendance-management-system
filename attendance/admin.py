from django.contrib import admin
from .models import (
    College,
    Department,
    Student,
    Staff,
    HOD,
    Attendance
)


admin.site.register(College)
admin.site.register(Department)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(HOD)
admin.site.register(Attendance)