from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Report, WaterLevel, CustomUser
import requests
import json
from geopy.geocoders import Nominatim
from django.core.mail import send_mail
from AFS_Group1 import settings
import yagmail

# Create your views here.

def report(request):
    return render(request, "report.html")

def report_details(request, id):

    report = Report.objects.get(id=id)
    context = {}
    context["report"] = report
    return render(request, "reportdetails.html", context)

def process_report_entry(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        picture_description = request.POST.get('picture_description')
        picture = request.FILES.get('picture')
        log = 0
        lat = 0

        if location:
            # calling the Nominatim tool and create Nominatim class
            loc = Nominatim(user_agent="Geopy Library")

            # entering the location name
            getLoc = loc.geocode(location)

            # printing address
            log = getLoc.longitude
            lat = getLoc.latitude

        rep = Report(title=title, description=description, lon=log, lat=lat, picture=picture,
                     picture_description=picture_description, user_id=0)
        rep.save()

        return HttpResponse("Data sucessfully inserted!")
    else:
        return HttpResponse("Invalid request method!")


def index(request):
    return render(request, "main.html")


def register(request):
    if request.method == "POST":
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        password = request.POST["password"]
        password_repeat = request.POST["password_repeat"]
        email = request.POST["email"]

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        elif password != password_repeat:
            messages.info(request, "Passwords do not match!")
            return redirect("register")

        user = CustomUser.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        user.set_password(password)
        user.create_code()
        user.save()


        # Send email with verification code using yagmail
        yag = yagmail.SMTP('example.mail3119@gmail.com', 'zvna lahf ulgg erua')
        subject = "Your Verification Code"
        message = f"Hello {first_name},\n\nYour verification code is: {user.code}\n\nThank you!"
        yag.send(to=email, subject=subject, contents=message)

        return redirect ("verify")

    else:
        return render(request, "register.html")

def verify(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("code")

        #get specific user
        user = CustomUser.objects.get(email = email)

        if str(user.code) == code:
            user.is_verified = True
            user.save()
            return redirect("login")
        
        else:
            return render(request, "verify.html")

    return render(request, "verify.html")

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(request, email=email, password=password)

        if user:
            auth.login(request, user)
            return redirect("main")

        else:
            messages.info(request, "Invalid Email or Password")
            return redirect("login")

    else:
        return render(request, "login.html")


def water_level_data(request):
    # URL to fetch the water levels in GeoJSON format
    wfs_url = (
        "https://gis.lfrz.gv.at/wmsgw/?key=a64a0c9c9a692ed7041482cb6f03a40a&request=GetFeature&service=WFS&version=2.0.0&outputFormat=json&typeNames=inspire:pegelaktuell"
    )

    # Get the data from the WFS URL
    response = requests.get(wfs_url)
    data = response.json()  # GeoJSON data

    ################## Space for optional Data processing before sending it to frontend ##################

    return JsonResponse(data)  # Return the data as a JSON response to the frontend


def report_data(request):
    reports = serializers.serialize('json', Report.objects.all())
    reports = json.loads(reports)
    return JsonResponse(reports, safe=False, status=200)

