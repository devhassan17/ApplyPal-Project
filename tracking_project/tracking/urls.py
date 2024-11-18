from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView # Add this import
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Homepage URL
    path('universities/', login_required(views.university_list), name='university_list'),
    path('signup/', views.signup, name='signup'),  # Signup URL
    path('login/', LoginView.as_view(), name='login'),  # Login URL (default Django view)
    path('logout/', LogoutView.as_view(), name='logout'), # Logout URL
]
