from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
# from .models import UserProfile
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import pycountry
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .models import University
from django.http import JsonResponse
from .forms import UniversitySignUpForm
from django.views.decorators.csrf import csrf_exempt
from ipware import get_client_ip
import geoip2.database
import logging
from django.utils.timezone import now
from .models import Tracking
import json

from rest_framework.views import APIView
from .models import University, Appointment

# Set up logging
logger = logging.getLogger(__name__)

# Homepage view
def homepage(request):
    # Ensure the user is authenticated
    if request.user.is_authenticated:
        # Filter universities related to the logged-in user
        universities = University.objects.filter(user=request.user)
    else:
        # If the user is not authenticated, no universities are shown
        universities = None

    return render(request, 'home.html', {'universities': universities})

# View for listing universities
def university_list(request):
    # Check if the user is an admin (staff)
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to view this page.")

    universities = University.objects.all()
    return render(request, 'university_list.html', {'universities': universities})

# Signup View
def signup(request):
    if request.method == 'POST':
        form = UniversitySignUpForm(request.POST)
        if form.is_valid():
            # Create the User instance
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()

            # Create the associated University instance
            University.objects.create(
                user=user,
                name=user.username,  # Optional: Use username as the default name
                email=user.email,  # Ensure email is correctly set
                institution_name=form.cleaned_data['institution_name'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                calendly_link=form.cleaned_data['calendly_link'], 
                address=form.cleaned_data['address'],
            )

            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = UniversitySignUpForm()

    return render(request, 'signup.html', {'form': form})



def generate_tracking_script(request, university_id):
    # Retrieve the university object based on the provided ID
    university = get_object_or_404(University, id=university_id)
    
    # Get the absolute URL for the tracking endpoint
    track_click_url = request.build_absolute_uri('https://signup.applypal.io/track-click/')
    
    # Get the Calendly URL (can be dynamic if needed)
    calendly_url = university.calendly_link or "https://calendly.com/example"

    # Insert the script into a template-friendly string format
    script_code = f"""
    <script src="https://www.google.com/recaptcha/enterprise.js?render=6LfKxIcqAAAAAL8e5CJP0PiZeD5rwuDwalyYnnl4"></script>
        <style>
        .grecaptcha-badge {{
            visibility: hidden;
            opacity: 0;
        }}
    </style>
        <script>
            function onClick() {{
                grecaptcha.enterprise.ready(async () => {{
                const token = await grecaptcha.enterprise.execute('6LfKxIcqAAAAAL8e5CJP0PiZeD5rwuDwalyYnnl4', {{action: 'LOGIN'}});
            }});
        }}
    </script>
    <script>

    document.addEventListener('DOMContentLoaded', function () {{
        fetch('https://ipinfo.io/json?token=4b143e6e51301d')
            .then(response => response.json())
            .then(data => {{
                const ip = data.ip;
                const country = data.country;                
                const trackClickUrl = '{track_click_url}';
                const logToConsole = (message) => console.log(message);
                const sendTrackingData = (type) => {{
                    const trackingData = {{ type, hash:"{university_id}", ip, country }}; 
                    fetch(trackClickUrl, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(trackingData),
                    }})
                        .then(response => response.json())
                        .then(result => logToConsole(`Response: ${{JSON.stringify(result)}}`))
                        .catch(error => logToConsole(`Error sending tracking data: ${{error}}`));
                }};
                const chatButton = document.createElement('button');
                chatButton.innerText = 'Chat to our Students';
                chatButton.style.cssText = `
                    position: fixed;
                    top: 50%;
                    right: 18px; 
                    transform: translateY(-50%) rotate(-90deg);
                    transform-origin: right center;
                    padding: 10px 20px;
                    background: #131e42;
                    color: white;
                    border: none;
                    border-radius: 0 5px 5px 0;
                    cursor: pointer;
                    z-index: 1000;
                `;
                const panel = document.createElement('div');
                panel.style.cssText = `
                    position: fixed;
                    top: 60%;
                    right: -310px;
                    transform: translateY(-50%);
                    width: 300px;
                    background: white;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 20px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    transition: right 0.3s ease;
                    z-index: 1001;
                    display: none;
                `;
                panel.innerHTML = `
                    <p>Would you like to book an appointment with one of our current students or alumni?</p>
                    <button id="yesButton" style="margin-right: 10px; padding: 5px 10px;  color: black; border: none; border-radius: 3px; cursor: pointer;">Yes</button>
                    <button id="noButton" style="padding: 5px 10px;  color: black; border: none; border-radius: 3px; cursor: pointer;">No</button>
                    <div style="text-align: center; margin-top: 20px; font-size: 12px;">
                    <a href="https://www.applypal.io/" target="_blank" style="text-decoration: none; color: #131e42;">Powered by TAG</a>
                </div>
                `;
                document.body.appendChild(panel);
                const togglePanel = (show) => {{
                    panel.style.right = show ? '0' : '-310px';
                }};
                chatButton.onclick = () => {{
                    onClick()
                    panel.style.display = 'block';
                    togglePanel(true);
                    sendTrackingData('chat');
                }};
                panel.querySelector('#yesButton').onclick = () => {{
                    window.open('{calendly_url}', '_blank');
                    sendTrackingData('calendly');
                }};
                panel.querySelector('#noButton').onclick = () => {{
                    togglePanel(false);
                    setTimeout(() => {{
                        panel.style.display = 'none';
                    }}, 300);
                    sendTrackingData('no');
                }};
                document.body.appendChild(chatButton);
            }})
            .catch(error => console.error('Error fetching IP info:', error));
    }});
</script>
    """
    
    # Render the script in a template
    return render(request, 'tracking_script.html', {'script_code': script_code})

def get_country_name(country_code):
    """
    Converts ISO country code to full country name.
    """
    try:
        country = pycountry.countries.get(alpha_2=country_code)
        return country.name if country else "Unknown"
    except Exception as e:
        return "Unknown"


# Track click events
@csrf_exempt
def track_click(request):
    if request.method == 'POST':
        try:
            # Parse incoming data
            data = json.loads(request.body)
            university_id = data.get('hash')
            interaction_type = data.get('type', 'no')

            # Get IP and Country
            ip = data.get('ip')
            country_code = data.get('country')
            
            country_name = get_country_name(country_code)
            
            # Fetch University
            university = get_object_or_404(University, id=university_id)

            # Save to Tracking model
            tracking_record = Tracking.objects.create(
                university=university,
                interaction_type=interaction_type,
                ip_address=ip if ip else "127.0.0.1",
                country=country_name,
                time=now()
            )

            # Prepare message with timestamp
            message = (
                f"Button clicked - University ID: {university_id}, Interaction Type: {interaction_type}, "
                f"IP: {ip}, Country: {country_name}, Time: {tracking_record.time}"
            )
            print(message)
            logger.info(message)

            return JsonResponse({
                "status": "success",
                "message": "Data tracked successfully.",
                "data": {
                    "university_id": university_id,
                    "interaction_type": interaction_type,
                    "ip_address": ip,
                    "country": country_name,
                    "time": tracking_record.time
                }
            })

        except Exception as e:
            logger.error(f"Error processing click: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=400)
        
def tracking_view(request):
    if request.user.is_staff:  # Admins can see all tracking records
        tracking_records = Tracking.objects.all()
    else:  # Regular users see only their university's tracking records
        tracking_records = Tracking.objects.filter(university__user=request.user)

    return render(request, 'tracking.html', {'tracking_records': tracking_records})
class UniversityDetailView(LoginRequiredMixin, DetailView):
    model = University
    template_name = 'university_detail.html'

    def get_object(self):
        # Fetch the University object based on the logged-in user
        try:
            # Assuming the `University` table has a `user` field that links it to the logged-in user
            return University.objects.get(user=self.request.user)
        except University.DoesNotExist:
            # Redirect the user to the edit page if no record exists
            return redirect('university_edit')    
class UniversityUpdateView(LoginRequiredMixin, UpdateView):
    model = University
    fields = ['name', 'email', 'calendly_link', 'institution_name', 'first_name', 'last_name', 'address']
    template_name = 'university_update.html'
    success_url = reverse_lazy('university_detail')  # Replace with your URL name for the detail page

    def get_object(self):
        # Ensure the user can only edit their own information
        return get_object_or_404(University, user=self.request.user)

    def form_valid(self, form):
        # Add any additional processing here if needed
        if self.request.user != form.instance.user:
            return HttpResponseForbidden("You are not allowed to edit this profile.")
        return super().form_valid(form)
def university_and_password_view(request):
    # Get all universities
    universities = University.objects.all()

    # Get the logged-in user
    user = request.user

    # Retrieve the user's password hash (this is just for demonstration purposes)
    password_hash = user.password  # It's better not to expose this in a real scenario

    # Pass the universities and password_hash to the template
    return render(
        request,
        'university_password_display.html',
        {'universities': universities, 'password_hash': password_hash}
    )