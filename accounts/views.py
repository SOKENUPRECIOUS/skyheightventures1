from django.shortcuts import render
from django.contrib.auth.models import User 
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings



# Create your views here.

def register(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username Taken")
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Used")
                return redirect('register')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=firstname,
                    last_name=lastname
                )
                user.save()
                messages.success(request, "Account Created")

                # --- Send Welcome Email ---
                subject = "Welcome to Sky Height Ventures 🎉"
                from_email = settings.DEFAULT_FROM_EMAIL  # defined in settings.py
                to = [user.email]

                # Load and render template with context
                template = get_template("emails/welcome.html")
                context = {
                    "username": user.first_name or user.username,
                    "site_url": getattr(settings, "SITE_URL", "http://127.0.0.1:8000"),
                }
                message = template.render(context)

                # Create the email
                msg = EmailMessage(subject, message, from_email, to)
                msg.content_subtype = "html"  # send as HTML
                msg.send()

                return redirect('signin')
        else:
            messages.info(request, "Passwords do not match")
            return redirect('register')

    return render(request, 'auth/signup.html')
def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('signin')
    
    return render(request,'auth/login.html')

@login_required
def dashboard(request):
    return render(request, 'auth/my-account.html')

def signout(request):
    logout(request)
    return redirect('signin' )

def welcome(request):
    return render(request, 'emails/welcome.html')