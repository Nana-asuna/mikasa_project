from django.contrib import admin
from .models import *

for model in [Donation, DonationCampaign]:
    admin.site.register(model) 