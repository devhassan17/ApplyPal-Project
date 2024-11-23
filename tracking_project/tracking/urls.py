from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView 
from django.contrib.auth.decorators import login_required
from . import views
from .views import generate_tracking_script, tracking_view , UniversityUpdateView, UniversityDetailView

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Homepage URL
    path('universities/', login_required(views.university_list), name='university_list'),  # University list
    path('signup/', views.signup, name='signup'),  # Signup URL
    path('login/', LoginView.as_view(), name='login'),  # Login URL
    path('logout/', LogoutView.as_view(), name='logout'),  # Logout URL
    path('generate-tracking-script/<str:university_id>/', login_required(views.generate_tracking_script), name='generate_tracking_script'),  # Tracking script
    path('track-click/', views.track_click, name='track_click'), 
    path('tracking/', login_required(views.tracking_view), name='tracking'),# Track button clicks
    path('university-password/', views.university_and_password_view, name='university_and_password'),
    path('profile/', UniversityDetailView.as_view(), name='university_detail'),
    path('profile/edit/', UniversityUpdateView.as_view(), name='university_edit'),# Calendly webhook
]
