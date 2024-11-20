from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from . import views
from .views import generate_tracking_script

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Homepage URL
    path('universities/', login_required(views.university_list), name='university_list'),  # University list
    path('signup/', views.signup, name='signup'),  # Signup URL
    path('login/', LoginView.as_view(), name='login'),  # Login URL
    path('logout/', LogoutView.as_view(), name='logout'),  # Logout URL
    path('generate-tracking-script/<int:university_id>/', login_required(views.generate_tracking_script), name='generate_tracking_script'),  # Tracking script
    path('track-click/', views.track_click, name='track_click'),  # Track button clicks
    path('calendly-webhook/', views.CalendlyWebhook.as_view(), name='calendly_webhook'),  # Calendly webhook
]
