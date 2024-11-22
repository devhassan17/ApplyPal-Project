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
    return render(request, 'home.html')

# View for listing universities
def university_list(request):
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
    track_click_url = request.build_absolute_uri('/track-click/')
    
    # Define the Calendly URL (can be dynamic if needed)
    calendly_url = university.calendly_link or "https://calendly.com/default"  
    
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
    chatButton.style.cssText = `
                    position: fixed;
                    top: 50%;
                    right: 18px; 
                    transform: translateY(-50%) rotate(-90deg);
                    transform-origin: right center;
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
            university_id = data.get('universityId')
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
        
def tracking_view(request):
    if request.user.is_staff:  # Admins can see all tracking records
        tracking_records = Tracking.objects.all()
    else:  # Regular users see only their university's tracking records
        tracking_records = Tracking.objects.filter(university__user=request.user)

    return render(request, 'tracking.html', {'tracking_records': tracking_records})
# def store_tracking_data(request):
#     if request.method == "POST":
#         try:
#             # Debugging input data
#             print(f"Request Data: {request.POST}")
#             data = request.POST
#             university_id = data.get("university_id")
#             interaction_type = data.get("interaction_type", "no")
#             ip_address = request.META.get('REMOTE_ADDR', "127.0.0.1")
#             country = data.get("country", "Unknown")
            
#             # Ensure the University exists
#             university = get_object_or_404(University, id=university_id)
            
#             # Save to Tracking Model
#             tracking_record = Tracking.objects.create(
#                 university=university,
#                 interaction_type=interaction_type,
#                 ip_address=ip_address,
#                 country=country
#             )
#             print(f"Tracking Record Saved: {tracking_record}")
            
#             return JsonResponse({"status": "success", "message": "Data saved successfully."}, status=201)
#         except Exception as e:
#             print(f"Error occurred: {e}")
#             return JsonResponse({"status": "error", "message": str(e)}, status=400)
#     else:
#         return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)
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
