from django.contrib import admin
from .models import *

for model in [Event, Task, Availability, Shift, Schedule]:
    admin.site.register(model) 