from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import UserProfile
from django.http import JsonResponse
from .forms import UserProfileForm
from django.views.decorators.csrf import csrf_exempt
from ipware import get_client_ip
import geoip2.database
import logging
import json

from rest_framework.views import APIView
from .models import University, Appointment

# Set up logging
logger = logging.getLogger(__name__)

# Homepage view
def homepage(request):
    return render(request, 'home.html')

# View for listing universities
def university_list(request):
    universities = University.objects.all()
    return render(request, 'university_list.html', {'universities': universities})

# Signup View
def signup(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        user_form = UserCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'signup.html', {'user_form': user_form, 'profile_form': profile_form})
# Generate tracking script for a university
from django.shortcuts import get_object_or_404, render

def generate_tracking_script(request, university_id):
    # Retrieve the university object based on the provided ID
    university = get_object_or_404(University, id=university_id)
    
    # Get the absolute URL for the tracking endpoint
    track_click_url = request.build_absolute_uri('/track-click/')
    
    # Define the Calendly URL (can be dynamic if needed)
    calendly_url = "https://calendly.com/example"
    
    # Insert the script into a template-friendly string format
    script_code = f"""
<script>
    document.addEventListener('DOMContentLoaded', function () {{
        const universityId = '{university_id}';
        const trackClickUrl = '{track_click_url}';

        const logToConsole = (message) => console.log(message);

        const sendTrackingData = (type) => {{
            const data = {{ type, universityId }};
            logToConsole(`Sending request data: ${{JSON.stringify(data)}}`);

            fetch(trackClickUrl, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(data),
            }})
            .then(response => response.json())
            .then(result => logToConsole(`Response: ${{JSON.stringify(result)}}`))
            .catch(error => logToConsole(`Error sending data: ${{error}}`));
        }};

        // Create the Chat to our Students button
        const button = document.createElement('button');
        button.innerText = 'Chat to our Students';
        button.style.cssText = `
            position: fixed;
            top: 50%;
            right: 0;
            transform: translateY(-50%);
            padding: 10px 20px;
            background: #007BFF;
            color: white;
            border: none;
            border-radius: 0 5px 5px 0;
            cursor: pointer;
            z-index: 1000;
        `;

        // Panel container
        const panel = document.createElement('div');
        panel.style.cssText = `
            position: fixed;
            top: 50%;
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
            <button id="yesButton" style="margin-right: 10px; padding: 5px 10px; background: #007BFF; color: white; border: none; border-radius: 3px; cursor: pointer;">Yes</button>
            <button id="noButton" style="padding: 5px 10px; background: #FF0000; color: white; border: none; border-radius: 3px; cursor: pointer;">No</button>
        `;

        // Append panel to body
        document.body.appendChild(panel);

        // Slide-in animation for panel
        const togglePanel = (show) => {{
            panel.style.right = show ? '0' : '-310px';
        }};

        // Button click to show panel
        button.onclick = () => {{
            panel.style.display = 'block';
            togglePanel(true);
            sendTrackingData('chat');
        }};

        // Yes button functionality
        panel.querySelector('#yesButton').onclick = () => {{
            window.open('{calendly_url}', '_blank');
            sendTrackingData('calendly');
        }};

        // No button functionality
        panel.querySelector('#noButton').onclick = () => {{
            togglePanel(false);
            setTimeout(() => {{
                panel.style.display = 'none';
            }}, 300);
            sendTrackingData('no');
        }};

        // Append button to body
        document.body.appendChild(button);
    }});
</script>
    """
    
    # Render the script in a template
    return render(request, 'tracking_script.html', {'script_code': script_code})


# Track click events
@csrf_exempt
def track_click(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            university_id = data.get('universityId')
            interaction_type = data.get('type')
            
            ip, _ = get_client_ip(request)
            country = "Unknown"
            if ip:
                try:
                    reader = geoip2.database.Reader('./GeoLite2-City.mmdb')
                    response = reader.city(ip)
                    country = response.country.name
                except Exception as e:
                    logger.error(f"GeoIP error: {e}")
            
            message = f"Button clicked - University ID: {university_id}, Interaction Type: {interaction_type}, IP: {ip}, Country: {country}"
            print(message)
            logger.info(message)
            return JsonResponse({"status": "success", "message": f"{interaction_type} button clicked."})
            
        except Exception as e:
            logger.error(f"Error processing click: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"error": "Invalid method"}, status=400)

# Calendly webhook to track appointments
class CalendlyWebhook(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            event_url = data.get('event_url')
            university = get_object_or_404(University, calendly_link=event_url)

            Appointment.objects.create(
                university=university,
                visitor_ip=data.get('ip_address', 'Unknown'),
                visitor_email=data.get('email'),
                appointment_date=data.get('start_time'),
            )
            return JsonResponse({"status": "success"})

        except json.JSONDecodeError:
            logger.error("Invalid JSON data in Calendly webhook")
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except University.DoesNotExist:
            logger.error("University not found for Calendly event URL")
            return JsonResponse({"error": "University not found"}, status=404)
        except Exception as e:
            logger.error(f"Unexpected error in Calendly webhook: {e}")
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)
