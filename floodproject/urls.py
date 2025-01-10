from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetDoneView, PasswordResetCompleteView
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
    path('vote-entry/<int:report_id>', views.process_vote_entry, name="process-vote-entry"),
    path('edit-vote/<int:report_id>', views.edit_vote, name="edit_vote"),
    path('submit-comment/<int:report_id>', views.submit_comment, name="submit_comment"),
    path('subscribe/<int:report_id>', views.toggle_subscribe, name="toggle_subscribe"),
    path("water-levels/", views.water_level_data, name='water_level_data'), # GeoJSON data URL
    path("reports/", views.report_data, name='report_data'),
    path("logout/", LogoutView.as_view(next_page="main"), name="logout"),
    path("verify/", views.verify, name="verify"),
    path("agent/tasks/",views.agent_tasks, name="agent_tasks"),
    path("agent/tasks/<int:task_id>/change_status/",views.change_task_status,name='change_status'),
    path("manager/tasks/",views.manager_tasks, name="manager_tasks"),
    path("manager/tasks/<int:task_id>/", views.task_details , name="task-details"),
    path("manager/tasks/<int:task_id>/update_task_description/", views.update_task_description, name="update_task_description"),
    path("manager/tasks/<int:task_id>/update_task_status/", views.update_task_status, name="update_task_status"),
    path("manager/tasks/<int:task_id>/update_task_agents/", views.update_task_agents, name="update_task_agents"),
    path("manager/tasks/<int:task_id>/promote_users/", views.promote_user, name="promote_user"),
    path("report/<int:report_id>/create_task/", views.create_task, name="create_task"),
    path('password_reset/', views.send_password_reset_email, name='password_reset'),
    path('password_reset_confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset_done/', views.password_reset_done, name='password_reset_done'),
    path('password_reset_complete/', views.password_reset_complete, name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)