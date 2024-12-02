from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from . import views

#urlpatterns is a variable that is used for the urls.py in the Quiz_Game folder 
#basically for pathing and rendering different templates
urlpatterns = [
    path("", views.index, name="main"),
    path("report/", views.report, name="report"),
    path("report/<int:id>", views.report_details, name="report-details"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path('report-entry/',views.process_report_entry,name="process-report-entry"),
    path("water-levels/", views.water_level_data, name='water_level_data'), # GeoJSON data URL
    path("reports/", views.report_data, name='report_data'),
    path("logout/", LogoutView.as_view(next_page="main"), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)