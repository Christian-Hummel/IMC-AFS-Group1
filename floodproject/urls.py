from django.urls import path
from . import views

#urlpatterns is a variable that is used for the urls.py in the Quiz_Game folder 
#basically for pathing and rendering different templates
urlpatterns = [
    path("", views.index, name="main"),
    path("report/", views.report, name="report"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path('report-entry/',views.process_report_entry,name="process-report-entry"),
    path("water-levels/", views.water_level_data, name='water_level_data'),  # GeoJSON data URL
]