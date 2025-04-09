from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('accounts/login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('', views.landing_page, name='landing_page'),  # New landing page route
    path('app/', views.home, name='home'),  # Move home to /app/
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('document/<int:document_id>/topics/', views.document_topics, name='document_topics'),
    path('document/<int:document_id>/summary/generate/', views.generate_summary, name='generate_summary'),
    path('summary/<int:summary_id>/', views.view_summary, name='view_summary'),
    path('summary/<int:summary_id>/flashcards/', views.flashcards, name='flashcards'),
    path('summary/<int:summary_id>/flashcards/generate/', views.generate_flashcards, name='generate_flashcards'),
    path('document/<int:document_id>/chatbot/', views.chatbot, name='chatbot'),
    path('document/<int:document_id>/knowledge-base/create/', views.create_knowledge_base, name='create_knowledge_base'),
    path('document/<int:document_id>/chat/message/', views.chat_message, name='chat_message'),
]