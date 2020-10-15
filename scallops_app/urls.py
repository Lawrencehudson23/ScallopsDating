from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('register/', views.process_registration),
    path('process/login/', views.process_login),
    path('logout/', views.process_logout),
    path('about_us/', views.display_about_us),
    path('contact_us/', views.display_contact_us),
    path('registration/', views.display_registration),
    path('login/', views.display_login),
    path('profile/', views.display_profile),
    path('edit/profile/', views.display_edit_profile),
    path('process/profile/', views.process_profile),
    path('like/', views.like),
    path('1on1/', views.display_1on1),
    path('like/', views.like),
    path('chat/index/', views.chat_index),
    path('chat/<str:room_name>/<int:user_id>/', views.toRoom),
    path('chat/<str:room_name>/<int:user_id>/<int:match_id>', views.room),
    path('single/', views.display_single),
    path('skip/', views.skip),
    path('matches/', views.match_list),
]
