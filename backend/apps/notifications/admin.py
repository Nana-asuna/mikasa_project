from django.contrib import admin
from .models import *

for model in [Notification, NotificationTemplate, NotificationPreference]:
    admin.site.register(model) 