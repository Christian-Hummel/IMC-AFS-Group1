from django.shortcuts import render, redirect, reverse , get_object_or_404
from django.contrib.auth.models import auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Report, Vote, CustomUser, Comment, Subscription, Task
import requests
import json
from geopy.geocoders import Nominatim
from django.core.mail import send_mail
from AFS_Group1 import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
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

def agent_tasks(request):
    if request.user.is_authenticated and request.user.role == 'agent':
        tasks = Task.objects.filter(agentID=request.user)
        return render(request, 'agent_tasks.html',{'tasks':tasks})

def manager_tasks(request):
    if request.user.is_authenticated and request.user.role == 'manager':
        tasks = Task.objects.filter(managerID=request.user)
        return render(request, 'manager_tasks.html', {'tasks': tasks})

def task_details(request,task_id):
    task = get_object_or_404(Task, id=task_id)
    assigned_agents = task.agentID.all()
    available_agents = CustomUser.objects.filter(role='agent').exclude(id__in=assigned_agents.values_list('id'))
    user = CustomUser.objects.filter(role='user')
    if request.user in task.agentID.all() or request.user == task.managerID:

        return render(request, 'detailed_task.html', {'task':task, 'assigned_agents':assigned_agents, 'available_agents':available_agents, 'user':user})



def change_task_status(request,task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user in task.agentID.all():
        task.status = Task.Status.DONE
        task.save()
    return redirect('agent_tasks')

def promote_user(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        user_id = request.POST.get('user')
        if user_id:
            user = get_object_or_404(CustomUser, id=user_id)
            user.role = 'agent'
            user.save()

    return redirect('task-details', task_id=task_id)


def update_task_description(request,task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user in task.agentID.all() or request.user == task.managerID:
        if request.method == 'POST':
            new_description = request.POST.get('description')
            if new_description:
                task.description = new_description
                task.save()

    return redirect('task-details', task_id=task.id)

def update_task_status(request,task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user  in task.agentID.all() or request.user == task.managerID:
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status:
                task.status = new_status
                task.save()

    return redirect('task-details', task_id=task.id)

def update_task_agents(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user in task.agentID.all() or request.user == task.managerID:
        if request.method == 'POST':
            agent_id = request.POST.get('agent')
            if agent_id:
                agent = get_object_or_404(CustomUser, id=agent_id, role='agent')
                task.agentID.add(agent)

    return redirect('task-details', task_id=task.id)

def create_task(request, report_id):
    report = Report.objects.get(id=report_id)

    if request.method == 'POST':
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        agent_id = request.POST.geT('agent')


        agent = CustomUser.objects.get(id=agent_id)



        task = Task.objects.create(description=description, managerID=request.user, reportID=report, due_date=due_date, status=Task.Status.TO_DO)

        if agent:
            task.agentID.add(agent)

        return redirect('report_detail', report_id=report.id)


def report_details(request, id):

    context = {}
    report = Report.objects.get(id=id)
    available_agents = CustomUser.objects.filter(role='agent').exclude(agents_tasks__reportID=report)
    subscriptions = [subscription.user_id_id for subscription in Subscription.objects.filter(report_id=id, active=True)]
    context["report"] = report
    context["subscriptions"] = subscriptions
    context["priority"] = ["manager", "superadmin"]


    if request.user.id:

        # fetch Vote model from database
        all_report_votes = Vote.objects.filter(report_id_id=id)
        # fetch user ids and pass it to context as a list
        users = [review.user_id_id for review in all_report_votes]
        # fetch Comment model from database
        all_comments = Comment.objects.filter(report_id_id=id).order_by("-date")

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
        context["comments"] = all_comments
        context["available_agents"] = available_agents


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

        # automatic first subscriber upon creation of a report

        subscription = Subscription(report_id_id=rep.id, user_id_id=request.user.id)

        subscription.save()

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


def agent(request):
    return render(request, "agent_tasks.html")


def register(request):
    if request.method == "POST":
        first_name = request.POST["firstname"].strip()
        last_name = request.POST["lastname"].strip()
        password = request.POST["password"]
        password_repeat = request.POST["password_repeat"]
        email = request.POST["email"]
        role = request.POST["role"]



        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)

            # overwrite user if email is not verified
            if not user.is_verified:
                user.first_name = first_name
                user.last_name = last_name
                user.password = password
                user.role = role
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
            first_name=first_name.capitalize(),
            last_name=last_name.capitalize(),
            password=password,
            role=role,
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

# function to extract references and pass them with bold html tags to view
def check_reference(text, user_id):
    # iterating over the contents of the comment for references

    i = 0
    while i < len(text):

        if text[i] == "@":
            fraction = text[i::].split(" ", maxsplit=2)

            if len(fraction) > 1:
                firstname = fraction[0][1::]
                lastname = fraction[1]


                if CustomUser.objects.filter(first_name=firstname.capitalize(), last_name=lastname.capitalize()).exists():

                    user = CustomUser.objects.filter(first_name=firstname.capitalize(), last_name=lastname.capitalize()).first()

                    #author of a post should not be able to reference him or herself
                    if user.id != user_id:

                        #space to add notification functionality here

                        original = f"@{firstname} {lastname}"
                        bold = f"<b>{firstname.capitalize()} {lastname.capitalize()}</b>"

                        text = text.replace(original, bold)

        i += 1

    return text



def submit_comment(request, report_id):
    if request.method == "POST":

        context = {}

        text = check_reference(request.POST.get("textcomment"), request.user.id)

        username = " ".join([request.user.first_name, request.user.last_name])

        comment = Comment.objects.create(comment=text, report_id_id=report_id,user_id_id=request.user.id, username=username)

        comment.save()

        context["comment"] = comment

        return render(request, 'singlecomment.html', context)
    else:
        return HttpResponse("Invalid request method!")


# function to subscribe to a report
def toggle_subscribe(request, report_id):
    if request.method == "GET":

        if Subscription.objects.filter(user_id_id=request.user.id, report_id_id=report_id):

            subscription = Subscription.objects.get(user_id_id=request.user.id, report_id_id=report_id)

            if subscription.active:

                subscription.active = False
                subscription.save()


            else:

                subscription.active = True
                subscription.save()

        else:


            subscription = Subscription.objects.create(user_id_id=request.user.id, report_id_id=report_id)

            subscription.save()


        return HttpResponse("Subscription updated succesfullly")
    else:
        return HttpResponse("Invalid request method!")


User = get_user_model()

def send_password_reset_email(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            # Check if the user exists with this email
            user = User.objects.get(email=email)

            # Create a token for the user
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)

            # Create the reset URL with the token
            reset_url = request.build_absolute_uri(reverse('password_reset_confirm', args=[user.pk, token]))

            # Send the email with the reset URL
            yag = yagmail.SMTP('example.mail3119@gmail.com', 'selin.meseli@gmail.com')  # Gmail credentials
            subject = "Password Reset Request"
            message = f"Hello {user.first_name},\n\nClick the link below to reset your password:\n{reset_url}\n\nThank you!"
            yag.send(to=email, subject=subject, contents=message)

            # Redirect to the 'password_reset_done' page
            return redirect("password_reset_done")

        except User.DoesNotExist:
            # If email does not exist in the database
            messages.error(request, "This email address is not registered.")
            return redirect("password_reset")


    return render(request, "registration/password_reset_form.html")