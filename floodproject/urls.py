from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.conf import settings
from django.conf.urls.static import static
from . import views

#urlpatterns is a variable that is used for the urls.py in the Quiz_Game folder 
#basically for pathing and rendering different templates
urlpatterns = [
    path("", views.index, name="main"),
    path("report/", views.report, name="report"),
    path("report/<int:id>", views.report_details, name="report-details"), # Report details
    path("reports/", views.report_data, name='report_data'),
    path('report-entry/', views.process_report_entry, name="process-report-entry"),
    path('report-entry/vote/', views.process_vote_entry, name="process-vote-entry"),
    path('report-entry/vote/edit/', views.edit_vote, name="edit-vote"),
    path("report/delete/<int:id>", views.delete_report, name="delete-report"),
    path("report/delete/error/", views.delete_report, name="delete-report-error"),
    path("report/create/", views.process_report_entry, name="create-report"),
    path("report/<int:report_id>/create_task/", views.create_task, name="create_task"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path('profile/',views.profile,name="profile"),
    path('profile/notification/<int:notification_id>', views.notification_details, name="notification-details"),
    path('profile/setread/<int:notification_id>',views.set_read,name="set-read"),
    path('profile/setunread/<int:notification_id>', views.set_unread, name="set-unread"),
    path('profile/deletenotif/<int:notification_id>', views.delete_notification, name="delete-notification"),
    path('vote-entry/<int:report_id>', views.process_vote_entry, name="process-vote-entry"),
    path('edit-vote/<int:report_id>', views.edit_vote, name="edit_vote"),
    path('subscribe/<int:report_id>', views.toggle_subscribe, name="toggle_subscribe"),
    path('submit-comment/<int:report_id>', views.submit_comment, name="submit_comment"),
    path("water-levels/", views.water_level_data, name="water_level_data"), # GeoJSON data URL
    path("water-levels/<int:hzb>", views.prev_water_levels, name='prev_water_levels'), # Historic water Levels
    path("water-levels/watererror", views.prev_water_levels, name='water_level_error'), # Error page for missing data
    path("reports/", views.report_data, name="report_data"),
    path('password_reset/', views.send_password_reset_email, name="password_reset"),
    path('password_reset_confirm/', views.password_reset_confirm, name="password_reset_confirm"),
    path('password_reset_done/', views.password_reset_done, name="password_reset_done"),
    path('password_reset_complete/', views.password_reset_complete, name="password_reset_complete"),
    path("logout/", LogoutView.as_view(next_page="main"), name="logout"),
    path("verify/", views.verify, name="verify"),
    path("agent/tasks/",views.agent_tasks, name="agent_tasks"),
    path("agent/tasks/<int:task_id>/change_status/",views.change_task_status,name="change_status"),
    path("manager/tasks/",views.manager_tasks, name="manager_tasks"),
    path("manager/tasks/<int:task_id>", views.task_details , name="task-details"),
    path("manager/tasks/<int:task_id>/update_task_description/", views.update_task_description, name="update_task_description"),
    path("manager/tasks/<int:task_id>/update_task_status/", views.update_task_status, name="update_task_status"),
    path("manager/tasks/<int:task_id>/update_task_agents/", views.update_task_agents, name="update_task_agents"),
    path("manager/tasks/<int:task_id>/send_email_invite/", views.send_email_invite, name="send_email_invite"),
    path('password_reset/', views.send_password_reset_email, name="password_reset"),
    path('password_reset_confirm/', views.password_reset_confirm, name="password_reset_confirm"),
    path('password_reset_done/', views.password_reset_done, name="password_reset_done"),
    path('password_reset_complete/', views.password_reset_complete, name="password_reset_complete"),
    path('password_update/', views.password_update, name="password_update"),
    path('password_update_success/', views.password_update_success, name="password_update_success"),
    path('location_update/', views.location_update, name="location_update"),
    path('location_update_success/', views.location_update_success, name="location_update_success"),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)