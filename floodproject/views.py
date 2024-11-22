from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Report, WaterLevel

# Create your views here.

def report(request):
    return render(request,"report.html")

def process_report_entry(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        rep = Report(title=title,description=description)
        rep.save()

        return HttpResponse("Data sucessfully inserted!")
    else:
        return HttpResponse("Invalid request method!")



def index(request):
    waterlevels = list(WaterLevel.objects.values('latitude', 'longitude', 'measuring_point', 'value', 'unit'))
    context = {'waterlevels':waterlevels}
    return render(request, "main.html", context)

def register(request):
    return render(request, "register.html")

def login(request):
    return render(request, "login.html")

# def report(request):
#     return render(request, "report.html")