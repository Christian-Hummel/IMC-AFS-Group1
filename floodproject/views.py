from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Report, Vote, CustomUser
import requests
import json
from geopy.geocoders import Nominatim
from django.core.mail import send_mail
from AFS_Group1 import settings
import yagmail

# Create your views here.

def report(request):
    return render(request, "report.html")

def get_severity_score(num):

    if num == 1:
        return "Low Level"
    elif num == 2:
        return "Moderate Level"
    elif num == 3:
        return "Medium Level"
    elif num == 4:
        return "High Level"
    else:
        return "Critical Level"

def report_details(request, id):
    context = {}
    report = Report.objects.get(id=id)
    context["report"] = report
    if request.user.id:




        all_report_votes = Vote.objects.filter(report_id_id=id)
        users = [review.user_id_id for review in all_report_votes]

        votestats = {}

        if request.user.id in users:

            current_severity = [get_severity_score(review.rating) for review in all_report_votes if request.user.id == review.user_id_id][0]
            flag = ["yes" if request.user.id == review.user_id_id and review.validity == False else "no" for review in all_report_votes][0]

            context["current_severity"] = current_severity
            context["flag"] = flag

        votestats["num_ratings"] = len([review for review in all_report_votes])
        votestats["total_rating"] = sum([int(review.rating) for review in all_report_votes])
        votestats["flag_count"] = len([review.validity for review in all_report_votes if review.validity == False])


        context["users"] = users
        context["votestats"] = votestats


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
                     picture_description=picture_description, user_id=request.user.id)
        rep.save()

        return HttpResponse("Data sucessfully inserted!")
    else:
        return HttpResponse("Invalid request method!")

def process_vote_entry(request,report_id):
    if request.method == 'POST':
        sev_rating = request.POST.get("severityselect")
        validity = request.POST.get("invcheck")
        if not validity:
            validity = True
        vote = Vote(report_id_id=report_id, user_id_id=request.user.id,rating=sev_rating, validity=validity)

        vote.save()

        return HttpResponse("Vote sucessfully inserted!")
    else:
        return HttpResponse("Invalid request method!")


def edit_vote(request, report_id):


    if request.method == 'POST':

        current_vote_query = Vote.objects.filter(user_id_id=request.user.id, report_id_id=report_id)
        vote_id = current_vote_query.values('id')[0]["id"]

        current_vote = Vote.objects.get(id=vote_id)

        print(current_vote)

        current_rating = current_vote.rating
        current_validity = current_vote.validity

        new_rating = request.POST.get("severityselect")
        new_validity = request.POST.get("invcheck")

        if not new_validity:
            new_validity = True


        current_vote.rating = new_rating
        current_vote.validity = new_validity
        current_vote.save()

        return HttpResponse("Vote sucessfully edited")
    else:
        return HttpResponse("No changes to previous rating detected")



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
            user = CustomUser.objects.get(email=email)

            # overwrite user if email is not verified
            if not user.is_verified:
                user.first_name = first_name
                user.last_name = last_name
                user.password = password
                user.set_password(password)
                user.create_code()
                user.save()

                # Send email with verification code using yagmail
                yag = yagmail.SMTP('example.mail3119@gmail.com', 'zvna lahf ulgg erua')
                subject = "Your Verification Code"
                message = f"Hello {first_name},\n\nYour verification code is: {user.code}\n\nThank you!"
                yag.send(to=email, subject=subject, contents=message)

                request.session["user_code"] = str(user.code)
                return redirect("verify")

            else:
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

        if "user_code" in request.session:
            user.code = request.session["user_code"]

        if user.code == code:
            user.is_verified = True
            user.save()
            auth.login(request, user)
            return redirect("main")
        
        else:
            return render(request, "verify.html")

    return render(request, "verify.html")

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(request, email=email, password=password)

        if user and user.is_verified:
            auth.login(request, user)
            return redirect("main")

        elif user and not user.is_verified:
            user.create_code()
            yag = yagmail.SMTP('example.mail3119@gmail.com', 'zvna lahf ulgg erua')
            subject = "Your Verification Code"
            message = f"Hello {user.first_name},\n\nYour verification code is: {user.code}\n\nThank you!"
            yag.send(to=email, subject=subject, contents=message)
            request.session["user_code"] = str(user.code)
            return redirect("verify")

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

