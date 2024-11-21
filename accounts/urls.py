# accounts/urls.py

from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register_choice, name='register'),
    path('register/company/', views.register_company, name='register_company'),
    path('register/user/', views.register_user, name='register_user'),
    path('studies/', views.studies, name='studies'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload_file'),
    path('send-emails/', views.send_emails, name='send_emails'),
    path('contacts/', views.contact_list, name='contact_list'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/<str:date>/', views.calendar_day_view, name='calendar_day_view'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('studies/<int:study_id>/details/', views.study_details, name='study_details'),
    path('preview/<int:file_id>/', views.preview_file, name='preview_file'),
    path('add-email-account/', views.add_email_account, name='add_email_account'),
    path('email-accounts/', views.list_email_accounts, name='list_email_accounts'),
    path('email-account/edit/<int:account_id>/', views.edit_email_account, name='edit_email_account'),
    path('download-emails-zip/', views.download_emails_zip, name='download_emails_zip'),
    path('reclamar/', views.reclamar, name='reclamar'), 
    path('download_zip_session/<int:session_id>/', views.download_zip_session, name='download_zip_session'),
    path('delete_session/<int:session_id>/', views.delete_session, name='delete_session'),
    path('update_estado_contacto/', views.update_estado_contacto, name='update_estado_contacto'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('export_excel/<int:study_id>/', views.export_study_excel, name='export_study_excel'),
    path('print_pdf/<int:study_id>/', views.print_study_pdf, name='print_study_pdf'),
    path('print-selected-studies-pdf/', views.print_selected_studies_pdf, name='print_selected_studies_pdf'),
    path('delete_processed_file/<int:file_id>/', views.delete_processed_file, name='delete_processed_file'),
    path('delete_processing_session/<int:session_id>/', views.delete_processing_session, name='delete_processing_session'),
    path('preview_file/<int:file_id>/', views.preview_file, name='preview_file'),

    # Ruta para el Dashboard Administrativo
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

]
