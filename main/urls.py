from django.views.static import serve
from django.contrib import admin
from django.urls import path
from main import views, settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('next', views.get_next),
    path('success/<slug:id>', views.success),
    path('faq', views.faq),
    path('playlist', views.playlist),
    path('album/<slug:album_id>', views.search_album),
    path('playlist/<slug:playlist_id>', views.search_playlist),
    path('album', views.album),
    path('create_playlist', views.register_user),
    path('previous', views.get_previous)
]

