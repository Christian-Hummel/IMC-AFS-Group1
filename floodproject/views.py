from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import auth, User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Report, Vote, CustomUser, Comment, Subscription, Task, Notification
import requests
import json
from geopy.geocoders import Nominatim
from django.core.mail import send_mail
from AFS_Group1 import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
import yagmail
from django.urls import reverse

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
        tasks = Task.objects.filter(agent=request.user)
        return render(request, 'agent_tasks.html',{'tasks':tasks})

def manager_tasks(request):
    if request.user.is_authenticated and request.user.role == 'manager':
        tasks = Task.objects.filter(manager=request.user)
        return render(request, 'manager_tasks.html', {'tasks': tasks})

def task_details(request,task_id):
    task = get_object_or_404(Task, id=task_id)
    assigned_agents = task.agent.all()
    available_agents = CustomUser.objects.filter(role='agent').exclude(id__in=assigned_agents.values_list('id'))
    user = CustomUser.objects.filter(role='user')
    if request.user in task.agent.all() or request.user == task.manager:

        return render(request, 'detailed_task.html', {'task':task, 'assigned_agents':assigned_agents, 'available_agents':available_agents, 'user':user})



def change_task_status(request,task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user in task.agent.all():
        task.status = Task.Status.DONE
        task.save()
    return redirect('agent_tasks')


def send_email_invite(request, task_id):

    if request.method == "POST":
        email_address = request.POST.get('email_address')
        user = CustomUser.objects.get(email=email_address)

        task = Task.objects.get(id=task_id)
        report = Report.objects.get(id=task.report.id)

        if user:
            if user.role  in ["manager", "agent"]:
                title="You have been assigned for a task"

                notification = Notification.objects.create(title=title, description=task.description, user_id=user.id,
                                                           report_id=report.id)
                notification.save()

                task.agent.add(user)

            else:
                user.role = "agent"
                user.save()
                title = "You have been assigned for a task"

                # create Notification for this user
                notification = Notification.objects.create(title=title, description=task.description, user_id=user.id, report_id=report.id)
                notification.save()


                task.agent.add(user)

    return redirect('task-details', task_id=task_id)



def update_task_description(request,task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user in task.agent.all() or request.user == task.manager:
        if request.method == 'POST':
            new_description = request.POST.get('description')
            if new_description:
                task.description = new_description
                task.save()

    return redirect('task-details', task_id=task.id)

def update_task_status(request,task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user  in task.agent.all() or request.user == task.manager:
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status:
                task.status = new_status
                task.save()

    return redirect('task-details', task_id=task.id)

def update_task_agents(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user in task.agent.all() or request.user == task.manager:
        if request.method == 'POST':
            agent_id = request.POST.get('agent')
            if agent_id:
                agent = get_object_or_404(CustomUser, id=agent_id, role='agent')
                task.agent.add(agent)

    return redirect('task-details', task_id=task.id)

def create_task(request, report_id):
    report = Report.objects.get(id=report_id)


    if request.method == 'POST':
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        agent_id = request.POST.get('agent')


        agent = CustomUser.objects.get(id=agent_id)



        task = Task.objects.create(description=description, manager=request.user, report=report, due_date=due_date, status=Task.Status.TO_DO)

        if agent:
            task.agent.add(agent)

        return redirect('report_detail', report_id=report.id)


def report_details(request, id):

    context = {}
    report = Report.objects.get(id=id)
    available_agents = CustomUser.objects.filter(role='agent').exclude(agents_tasks__report=report)
    subscriptions = [subscription.user_id for subscription in Subscription.objects.filter(report_id=id, active=True)]
    context["report"] = report
    context["subscriptions"] = subscriptions
    context["priority"] = ["manager", "superadmin"]


    if request.user.id:

        # fetch Vote model from database
        all_report_votes = Vote.objects.filter(report_id=id)
        # fetch user ids and pass it to context as a list
        users = [review.user_id for review in all_report_votes]
        # fetch Comment model from database
        all_comments = Comment.objects.filter(report_id=id).order_by("-date")
        # fetch Notifications for user from database
        notifications = len(Notification.objects.filter(user_id=request.user.id, read=False))



        votestats = {}

        if request.user.id in users:

            current_severity = [get_severity_score(review.rating) for review in all_report_votes if request.user.id == review.user_id][0]
            flag = ["yes" if request.user.id == review.user_id and review.validity == False else "no" for review in all_report_votes][0]

            context["current_severity"] = current_severity
            context["flag"] = flag

        votestats["num_ratings"] = len([review for review in all_report_votes])
        votestats["total_rating"] = sum([int(review.rating) for review in all_report_votes])
        votestats["flag_count"] = len([review.validity for review in all_report_votes if review.validity == False])


        context["users"] = users
        context["votestats"] = votestats
        context["comments"] = all_comments
        context["available_agents"] = available_agents
        context["notifications"] = notifications


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

        user = CustomUser.objects.get(id=request.user.id)


        if location:
            # calling the Nominatim tool and create Nominatim class
            loc = Nominatim(user_agent="Geopy Library")

            # entering the location name
            getLoc = loc.geocode(location)

            # extract longitude and latitude
            log = getLoc.longitude
            lat = getLoc.latitude

        rep = Report(title=title, description=description, lon=log, lat=lat, picture=picture,
                     picture_description=picture_description, user_id=CustomUser.objects.get(id=user.id).id)
        rep.save()


        # automatic first subscriber upon creation of a report

        subscription = Subscription(report_id=rep.id, user_id=CustomUser.objects.get(id=user.id).id)

        subscription.save()


        return HttpResponse("Data sucessfully inserted!")
    else:
        return HttpResponse("Invalid request method!")


def delete_report(request, id):

    if request.user.role not in ["manager", "superadmin"]:

        report = Report.objects.get(id=id)

        tasks = Task.objects.filter(report_id=id)

        for task in tasks:
            if task.status != Task.Status.DONE:
                return HttpResponse("This Report cannot be deleted because of active tasks assigned to it.")

        report.delete()
        return render(request, "report_delete_success.html")

def process_vote_entry(request,report_id):
    if request.method == 'POST':
        sev_rating = request.POST.get("severityselect")
        validity = request.POST.get("invcheck")
        if not validity:
            validity = True
        vote = Vote(report_id=report_id, user_id=request.user.id,rating=sev_rating, validity=validity)

        vote.save()

        return HttpResponse("Vote sucessfully inserted!")
    else:
        return HttpResponse("Invalid request method!")


def edit_vote(request, report_id):


    if request.method == 'POST':

        current_vote_query = Vote.objects.filter(user_id=CustomUser.objects.get(id=request.user.id).id, report_id=report_id)
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
    context = {}

    notifications = len(Notification.objects.filter(user_id=request.user.id, read=False))

    context["notifications"] = notifications

    return render(request, "main.html", context)


def profile(request):
    context = {}

    notifications = Notification.objects.filter(user_id=request.user.id)

    geolocator = Nominatim(user_agent="Geopy Library")

    location = geolocator.reverse(f"{request.user.latitude}, {request.user.longitude}")

    context["home_address"] = location.address
    context["notifications"] = notifications

    return render(request, "userprofile.html", context)


def agent(request):
    return render(request, "agent_tasks.html")


def register(request):
    if request.method == "POST":
        first_name = request.POST["firstname"].strip()
        last_name = request.POST["lastname"].strip()
        address = request.POST["address"]
        password = request.POST["password"]
        password_repeat = request.POST["password_repeat"]
        email = request.POST["email"]
        role = request.POST.get("role","user")

        # calling the Nominatim tool and create Nominatim class
        loc = Nominatim(user_agent="Geopy Library")

        # entering the location name
        getLoc = loc.geocode(address)

        # Works only partially - many invalid cases will get some values assigned
        if not getLoc:
            return HttpResponse("Address not found")

        # printing address
        lng = getLoc.longitude
        lat = getLoc.latitude



        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)

            # overwrite user if email is not verified
            if not user.is_verified:
                user.first_name = first_name
                user.last_name = last_name
                user.latitude = lat
                user.longitude = lng
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
            latitude=lat,
            longitude=lng,
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
        email_prefill = request.GET.get("email", "")
        role_prefill = request.GET.get("role", "user")


        return render(request, "register.html", {
            "email_prefill": email_prefill,
            "role_prefill": role_prefill,
        })

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
def check_reference(text, user_id, report_id):
    # iterating over the contents of the comment for references

    current_user = CustomUser.objects.get(id=user_id)
    reflist = []

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

                        original = f"@{firstname} {lastname}"
                        bold = f"<b>{firstname.capitalize()} {lastname.capitalize()}</b>"

                        text = text.replace(original, bold)

                        # notification preparation

                        title = f"{current_user.first_name} {current_user.last_name} mentioned you in a comment"

                        description = text

                        notification = Notification.objects.create(title=title, description=description, user_id=user.id, report_id=report_id)
                        notification.save()

                        reflist.append(user.id)

        i += 1

    subscriptions = Subscription.objects.filter(report_id=report_id, active=True)

    for subscription in subscriptions:

        if subscription.user_id != user_id and subscription.user_id not in reflist:
            title = f"{current_user.first_name} {current_user.last_name} added a comment to a report"
            description = text

            notification = Notification(title=title, description=description, user_id=subscription.user_id,
                                        report_id=report_id)
            notification.save()



    return text



def submit_comment(request, report_id):
    if request.method == "POST":

        context = {}

        text = check_reference(request.POST.get("textcomment"), request.user.id, report_id)

        username = " ".join([request.user.first_name, request.user.last_name])

        comment = Comment.objects.create(comment=text, report_id=report_id,user_id=CustomUser.objects.get(id=request.user.id).id, username=username)

        comment.save()


        context["comment"] = comment

        return render(request, 'singlecomment.html', context)
    else:
        return HttpResponse("Invalid request method!")


# function to subscribe to a report
def toggle_subscribe(request, report_id):
    if request.method == "GET":

        if Subscription.objects.filter(user_id=request.user.id, report_id=report_id):

            subscription = Subscription.objects.get(user_id=request.user.id, report_id=report_id)

            if subscription.active:

                subscription.active = False
                subscription.save()


            else:

                subscription.active = True
                subscription.save()

        else:


            subscription = Subscription.objects.create(user_id=CustomUser.objects.get(id=request.user.id).id, report_id=report_id)

            subscription.save()


        return HttpResponse("Subscription updated succesfullly")
    else:
        return HttpResponse("Invalid request method!")



def send_password_reset_email(request):
    errors = []  # To collect errors

    if request.method == "POST":
        email = request.POST.get("email").strip()

        if not email:
            errors.append("Email field cannot be empty.")
        elif not CustomUser.objects.filter(email=email).exists():
            errors.append("No account found with this email address.")
        else:
            user = CustomUser.objects.get(email=email)
            reset_url = request.build_absolute_uri(reverse('password_reset_confirm') + f"?email={user.email}")
            yag = yagmail.SMTP('example.mail3119@gmail.com', 'zvna lahf ulgg erua')
            subject = "Password Reset Request"
            message = f"""Hello {user.first_name},

Click the link below to reset your password:
{reset_url}

If you didn't request this password reset, please ignore this email.

Thank you!"""
            yag.send(to=email, subject=subject, contents=message)
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect("password_reset_done")

    return render(request, "registration/password_reset_form.html", {'errors': errors})


def password_reset_confirm(request):
    email = request.GET.get('email')

    if not email:
        messages.error(request, "Invalid reset link.")
        return redirect('password_reset')

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, "No user found with this email.")
        return redirect('password_reset')

    errors = []  # Collect validation errors

    if request.method == "POST":
        password = request.POST.get("password")
        password_repeat = request.POST.get("password_repeat")

        if not password or not password_repeat:
            errors.append("Please fill in both password fields.")
        elif password != password_repeat:
            errors.append("Passwords do not match!")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if not errors:
            user.set_password(password)
            user.save()
            messages.success(request, "Your password has been successfully reset. You can now log in with your new password.")
            return redirect('password_reset_complete')

    # If there are errors or it's a GET request, render the form with errors
    return render(request, "registration/password_reset_confirm.html", {'email': email, 'errors': errors})

def password_reset_done(request):
    return render(request, "registration/password_reset_done.html")


def password_reset_complete(request):
    return render(request, "registration/password_reset_complete.html")

def password_update(request):
    if request.method == "POST":
        current_password = request.POST["currentpassword"]
        new_password = request.POST["newpassword"]
        password_repeat = request.POST["password_repeat"]

        if request.user.check_password(current_password):


            if new_password != password_repeat:
                return HttpResponse("Passwords do not match!")

            elif new_password == password_repeat and new_password == current_password:
                return HttpResponse("Please enter a password different from your current password")

            else:
                request.user.set_password(new_password)
                # add boolean value to prevent repeated editing of password, need to log in with new password first
                request.session["pwchange"] = True
                request.user.save()
                update_session_auth_hash(request, request.user)

                return redirect("password_update_success")

        else:
            return HttpResponse("Incorrect current password")


def password_update_success(request):
    return render(request, "password_update_success.html")


def location_update(request):
    if request.method == "POST":
        address = request.POST["newlocation"]

        # calling the Nominatim tool and create Nominatim class
        geolocator = Nominatim(user_agent="Geopy Library")

        # current address:

        current_address = geolocator.reverse(f"{request.user.latitude}, {request.user.longitude}")

        # entering the location name
        new_address = geolocator.geocode(address)


        # Works only partially - many invalid cases will get some values assigned
        if not new_address:
            return HttpResponse("Address not found")

        # extract longitude and latitude of address
        lng = new_address.longitude
        lat = new_address.latitude

        if current_address.address == new_address.address:
            return HttpResponse("Please enter a new address")

        else:
            request.user.longitude = lng
            request.user.latitude = lat
            # add boolean value to prevent editing of location multiple time in short time period
            # this constraint of 30 days as stated in the success html is not implemented just, a suggestion
            request.session["locationchange"] = True
            request.user.save()
            return redirect("location_update_success")



def location_update_success(request):
    return render(request, "location_update_success.html")


def notification_details(request, notification_id):
    context = {}

    notification = Notification.objects.get(id=notification_id)
    report = Report.objects.get(id=notification.report_id)

    context["notification"] = notification
    context["report"] = report


    return render(request, "singlenotification.html", context)


def set_read(request, notification_id):
    if request.method == "GET":


        notification = Notification.objects.get(id=notification_id)

        if notification.read:
            return HttpResponse("status already on read")

        else:
            notification.read = True
            notification.save()

            return HttpResponse("status set to read")

    else:
        return HttpResponse("Invalid request method!")

def set_unread(request, notification_id):
    if request.method == "GET":

        notification = Notification.objects.get(id=notification_id)

        if not notification.read:
            return HttpResponse("status already on unread")

        else:
            notification.read = False
            notification.save()

            return HttpResponse("status set to unread")

    else:
        return HttpResponse("Invalid request method!")

def delete_notification(request, notification_id):
    if request.method == "GET":

        notification = Notification.objects.get(id=notification_id)

        if notification:
            notification.delete()

            return HttpResponse("Notification has been sucessfully deleted")

        else:
            return HttpResponse("Notification not found")
    else:
        return HttpResponse("Invalid request method")