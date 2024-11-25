from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Report, WaterLevel
import requests

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