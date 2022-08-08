from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from gfg import settings
from django.contrib.sites.shortcuts import get_current_site, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . token import generate_token
from django.core.mail import EmailMessage, send_mail

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")


def signup(request):
    if request.method=="POST":
        username = request.POST["username"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        if User.objects.filter(username=username):
            messages.error(request, "username already exist please try another one")
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request, "username already exist please try another one")
            return redirect('home')

        if not username.isalnum:
            messages.error(request, "already exist please try another one")
            return redirect("home")

        if len(username)>10:
            messages.error(request, "username must be at least 10 characters1")
           

        if pass1 != pass2:
            messages.error(request, "passwords did not match")
            

        myuser = User.objects.create_user(username, email, pass1)
        myuser.firstname= fname
        myuser.lastname= lname
        myuser.is_active= False
        myuser.save()

        messages.success(request,"your account has been created. we have sent you an confirmation email please confirm your email address.")

        subject = "welcome to gfg - django-login"
        message = "hello"+myuser.firstname +"!! \n " + "welcome to gfg. \n thank you for visiting out website. \n we have sent you a confirmation email, please confirm your email address in order to activate your account. \n thank you \n abhishek."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)


        current_site = get_current_site(request)
        email_subject = "confirm your email address."
        message2 = render_to_string('email_confirmation.html',{
            "name" : myuser.firstname,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(myuser.pk)),
            "token": generate_token.make_token(myuser)})

        email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [myuser.email])
        email.fail_silently = True

        email.send()

        return redirect("signin")

    return render(request, "authentication/signup.html")


def signin(request):

    if request.method=="POST":
        username = request.POST["username"]
        pass1 = request.POST["pass1"]

        user=authenticate(username=username,password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html",{"fname":fname})
        else:
            messages.error(request, "bad credentials")


    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "logged out successfully")
    return redirect("home")



def activate(request, uidb64, token):
   
    try:
         uid = force_str(urlsafe_base64_decode(uidb64))
         myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active= True
        myuser.save()
        login(request, myuser)
        return redirect("home")
    else:
        return render(request, "activation_failed.html")