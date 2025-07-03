from django.contrib import admin
from .models import *

for model in [User, UserProfile, UserApprovalRequest, PasswordHistory, LoginAttempt]:
    admin.site.register(model) 