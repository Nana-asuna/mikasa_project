from django.contrib import admin
from .models import *

for model in [Report, ReportTemplate, Dashboard]:
    admin.site.register(model) 