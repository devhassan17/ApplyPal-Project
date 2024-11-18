from .models import University
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

# Homepage view
def homepage(request):
    return render(request, 'home.html')

# View for listing universities
def university_list(request):
    universities = University.objects.all()
    return render(request, 'university_list.html', {'universities': universities})

# Signup View
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after signup
            messages.success(request, f"Account created for {user.username}!")
            return redirect('homepage')  # Redirect to homepage or wherever
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})
