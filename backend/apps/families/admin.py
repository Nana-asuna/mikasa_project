from django.contrib import admin
from .models import *

for model in [Family, FamilyMember, Placement, FamilyVisit]:
    admin.site.register(model) 