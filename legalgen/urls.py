# Module: urls.py

# Import necessary libraries
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .get_data import post_advocate_details
from .views import (
    generate_legal_doc_wordfile,
    get_chat_history,
    signup_view,
    advocate_login_view,
    advocate_dashboard_view,
    save_client_data
)

# define path
urlpatterns = [
    path('', advocate_login_view, name='advocate_login'),
    path('signup/', signup_view, name='advocate_signup'),
    path('dashboard/', advocate_dashboard_view, name='advocate_dashboard'),
    path('generate_legal_doc_wordfile/', generate_legal_doc_wordfile, name='generate_legal_doc_wordfile'),
    path('get_chat_history/', get_chat_history, name='get_chat_history'),
    path('post_advocate_details/', post_advocate_details, name='post_advocate_details'),
    path("save_client_data/", save_client_data, name="save_client_data"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
