from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Dashboard & User Interface
    path('', views.index, name='index'), 
    path('set-nickname/', views.set_nickname, name='set_nickname'), 
    
    # 2. Private Chatting Features
    path('chat/<str:username>/', views.chat_room, name='chat_room'),
    path('clear-chat/<str:username>/', views.clear_chat, name='clear_chat'),
    path('block-user/<str:username>/', views.block_user, name='block_user'),
    
    # 3. Authentication (Signup/Login/Logout)
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # 4. Profile & Security
    # MAINE ISKA NAAM 'profile' KAR DIYA HAI TAAKI ERROR KHATAM HO JAYE
    path('profile/', views.profile, name='profile'),
    path('password-reset/', views.password_reset_simple, name='password_reset'),

   path('stranger-chat/', views.stranger_chat, name='stranger_chat'), 
   path("check-room/", views.check_room, name="check_room"), 
   path('clear-waiting/', views.clear_waiting, name='clear_waiting'), # 'name' add kar diya
   path('upload/', views.upload_file, name='upload_file'), 
   # 6. Media & Files (Media handling ke liye setup)
  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)