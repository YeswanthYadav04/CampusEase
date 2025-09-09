# chatbot/admin.py
from django.contrib import admin
from .models import Student, Lecture, AttendanceRecord

admin.site.register(Student)
admin.site.register(Lecture)
admin.site.register(AttendanceRecord)