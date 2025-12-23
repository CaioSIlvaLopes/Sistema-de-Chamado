
from django.contrib import admin
from django.urls import path
from tickets.views import tickets_view
from django.conf import settings
from django.conf.urls.static import static
from users.views import register_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chamados/', tickets_view,),
    path('register/', register_view, name='register'),
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)