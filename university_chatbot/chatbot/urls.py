from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('student-login/', views.student_login, name='student_login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('chat/', views.chat_interface, name='chat_interface'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('set-language/', views.set_language, name='set_language'),
    path('process-message/', views.process_message, name='process_message'),
    path('delete-document/<int:document_id>/', views.delete_document, name='delete_document'),
    path('delete-faq/<int:faq_id>/', views.delete_faq, name='delete_faq'),
    path('download-document/<int:document_id>/', views.download_document, name='download_document'),
    path('logout/', views.logout_view, name='logout'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)