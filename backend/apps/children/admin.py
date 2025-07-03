from django.contrib import admin
from .models import *

for model in [Child, MedicalRecord]:
    admin.site.register(model) 