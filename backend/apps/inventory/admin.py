from django.contrib import admin
from .models import *

for model in [InventoryItem, Supplier]:
    admin.site.register(model) 