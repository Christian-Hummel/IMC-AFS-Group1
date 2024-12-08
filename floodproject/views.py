from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Report
import requests
import json
import pandas as pd

from plotly.offline import plot
import plotly.express as px

#from plotly.graph_objs import Scatter

# Create your views here.

def report(request):
    return render(request,"report.html")

def report_details(request, id):

    report = Report.objects.get(id=id)
    context = {}
    context["report"] = report
    return render(request, "reportdetails.html", context)

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
    return render(request, "main.html")

def register(request):
    return render(request, "register.html")

def login(request):
    return render(request, "login.html")



def load_water_level_data():
    # URL to fetch the water levels in GeoJSON format
    wfs_url = (
        "https://gis.lfrz.gv.at/wmsgw/?key=a64a0c9c9a692ed7041482cb6f03a40a&request=GetFeature&service=WFS&version=2.0.0&outputFormat=json&typeNames=inspire:pegelaktuell"
    )

    # Get the data from the WFS URL
    response = requests.get(wfs_url)
    data = response.json()  # GeoJSON data

    return data

def water_level_data(request):

    data = load_water_level_data()

    ################## Space for optional Data processing before sending it to frontend ##################

    return JsonResponse(data)  # Return the data as a JSON response to the frontend

def report_data(request):

    reports = serializers.serialize('json', Report.objects.all())
    reports = json.loads(reports)
    return JsonResponse(reports,safe=False, status=200)



def prev_water_levels(request, hzb):

    current_data = load_water_level_data()

    #print(current_data)

    with open(r"floodproject/historical_data/historical.json","r") as file:
        plot_data = json.load(file)

    hzb = str(hzb)
    current_unit = ""

    # extract current water levels from json request data

    for dict in current_data["features"]:
        #print(f"first level {dict['properties']}")
        if str(dict["properties"]["hzbnr"]) == hzb:
            plot_data[hzb]["current_value"] = dict["properties"]["wert"]
            plot_data[hzb]["current_unit"] = dict["properties"]["einheit"]
            current_unit = plot_data[hzb]["current_unit"]

    # print(plot_data)

    df = pd.DataFrame({
        'year': plot_data[hzb]["years"],
        'value': plot_data[hzb]["values"]
    })



    fig = px.line(df, x='year', y='value')

    fig.update_layout(xaxis_title="years",
                      yaxis_title=f"level in {current_unit}",
                      modebar_remove=['pan','zoom'])

    plot_data[hzb]["plot"] = plot(fig, output_type='div')


    # Alternative way but with less options

    # x_data = plot_data[hzb]["years"]
    # y_data = plot_data[hzb]["values"]

    # plot_div = plot([Scatter(x=x_data, y=y_data,
    #
    #                          mode='lines', name='historic_water_data',
    #                          opacity=0.8, marker_color='green')],
    #                 output_type='div')

    # plot_data[hzb]["plot"] = plot_div


    return render(request, "waterdetails.html", context={'plot_data': plot_data[hzb]})


