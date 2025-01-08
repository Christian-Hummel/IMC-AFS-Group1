from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import Report, WaterLevel, CustomUser
import requests
import json
#edited while merging
import geopy
from geopy.geocoders import Nominatim
#=======
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
        location = request.POST.get('location')

        if location:

            # calling the Nominatim tool and create Nominatim class
            loc = Nominatim(user_agent="Geopy Library")

            # entering the location name
            getLoc = loc.geocode(location)

            # printing address
            log = getLoc.longitude
            lat = getLoc.latitude

            rep = Report(title=title, description=description, lon=log, lat=lat, user_id=0)
            rep.save()

        else:

            rep = Report(title=title,description=description, lon=1, lat=1, user_id=0)
            rep.save()

        return HttpResponse("Data sucessfully inserted!")
    else:
        return HttpResponse("Invalid request method!")



def index(request):
    return render(request, "main.html")

def register(request):
    if request.method == "POST":
        full_name = request.POST["name"]
        password = request.POST["password"]
        password_repeat = request.POST["password_repeat"]
        email = request.POST["email"]
        gender = request.POST["gender"]
        first_name = full_name.split()[0]
        last_name = full_name.split()[1]


        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        elif password != password_repeat:
            messages.info(request, "Passwords do not match!")
            return redirect("register")

        user = CustomUser.objects.create_user(
            email = email,
            first_name= first_name,
            last_name= last_name,
            gender = gender,
            password=password,
        )

        user.set_password(password)
        user.save()

        messages.success(request, 'Registration successful!')
        return redirect('login')

    else:
        return render(request, "register.html")

def login(request):
    if request.method == "POST":
        email= request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(request, email = email, password=password)

        if user:
            auth.login(request, user)
            return redirect("main")

        else:
            messages.info(request, "Invalid Email or Password")
            return redirect("login")

    else:
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

def build_code_response(code_nr):

    first_digit = [int(num) for num in str(code_nr)][0]

    if first_digit == 1:
        return "Low Water"
    elif first_digit == 2:
        return "Medium Water"
    elif first_digit == 3:
        return "Increased Water Flow"
    elif first_digit == 4:
        return "Flood Level 1"
    elif first_digit == 5:
        return "Flood Level 2"
    elif first_digit == 6:
        return "Flood Level 3"
    else:
        return "No Data"

def water_level_data(request):

    data = load_water_level_data()
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
    try:

        for dict in current_data["features"]:
            #print(f"first level {dict['properties']}")
            if str(dict["properties"]["hzbnr"]) == hzb:
                gesamtcode = dict["properties"]["gesamtcode"]
                plot_data[hzb]["danger_level"] = build_code_response(gesamtcode)
                plot_data[hzb]["current_value"] = dict["properties"]["wert"]
                plot_data[hzb]["current_unit"] = dict["properties"]["einheit"]
                current_unit = plot_data[hzb]["current_unit"]

                # print(plot_data)

                df = pd.DataFrame({
                    'year': plot_data[hzb]["years"],
                    'value': plot_data[hzb]["values"]
                })

                # Calculate all-time high and low
                all_time_high = df['value'].max()
                all_time_low = df['value'].min()

                # Calculate median and quartiles
                median_value = df['value'].median()
                q1 = df['value'].quantile(0.25)
                q3 = df['value'].quantile(0.75)

                fig = px.line(df, x='year', y='value')

                # Add all-time high and low to the plot
                fig.add_hline(y=all_time_high, line_dash="dash", line_color="red", annotation_text="All-Time High",
                              annotation_position="bottom right")
                fig.add_hline(y=all_time_low, line_dash="dash", line_color="blue", annotation_text="All-Time Low",
                              annotation_position="bottom right")

                # Add median and quartiles to the plot
                fig.add_hline(y=median_value, line_dash="dash", line_color="green", annotation_text="Median",
                              annotation_position="bottom right")
                fig.add_hline(y=q1, line_dash="dot", line_color="blue", annotation_text="Q1",
                              annotation_position="bottom right")
                fig.add_hline(y=q3, line_dash="dot", line_color="red", annotation_text="Q3",
                              annotation_position="bottom right")


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

    except:

        return render(request, "watererror.html")





