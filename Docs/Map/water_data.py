import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import json

dict = {}
mess_key = ""
value_start = 0

path = r"C:\Users\Chris\Desktop\Software_Engineering_Project\Oberflächengewässer\ehyd_messstellen_all_owf\Q-Monatsmaxima"
dirs = os.listdir(path)

counter = 0

for file in dirs:
    if file.endswith(".csv"):

        # count for amount of files succeeded
        counter += 1
        print(file)
        print(counter)



        # join base path with filename
        file_path = os.path.join(path, file)


        # read csv in pandas
        df = pd.read_csv(file_path, sep=';', encoding='latin-1', decimal=",")

        #extract name of the measuring point
        messstelle = df.columns[1]




        #first 30 values - extract some metadata

        for i in range(0, 30):

            # add HZB-Nummer as identifier
            if "HZB-Nummer" in df.iloc[i,0]:
                mess_key = int(df.iloc[i,1])
                dict[int(df.iloc[i,1])] = {}
                dict[mess_key]["messstelle"] = messstelle

            # store unit in dictionary
            if "Einheit" in df.iloc[i,0]:
                dict[mess_key]["einheit"] = "".join([x for x in df.iloc[i,1] if x not in ["[","]"]])

            # set counter for extracting water level values and timestamps
            if "Werte" in df.iloc[i,0]:
                value_start = i + 1


        #filter out rows with the value marked as "Lücke" - no value recorded for this date - replace them with 0


        for c in range(value_start, len(df)):
            if df.iloc[c, 1] in " Lücke":
                df.iloc[c, 1] = 0



        # replace commas with dots
        df = df.replace(regex={',': '.'})

        # convert strings to float in this column
        df.iloc[value_start:,1] = df.iloc[value_start:,1].astype(float)

        # remove hours/minutes/seconds of date columns
        df.iloc[value_start:,0] = df.iloc[value_start:,0].apply(lambda x: x.split(" ")[0])



        date_json = {}

        # edit time format and convert values to float before adding it to date_json

        for x in range(value_start, len(df)):
            if df.iloc[x,0].split(".")[2] not in date_json.keys():
                date_json[df.iloc[x,0].split(".")[2]] = df.iloc[x,1]

            if df.iloc[x,1] > date_json[df.iloc[x,0].split(".")[2]]:
                date_json[df.iloc[x,0].split(".")[2]] = df.iloc[x,1]




        #insert years to dictionary
        dict[mess_key]["years"] = [int(key) for key, value in date_json.items() if value > 0]

        #insert values to dictionary
        dict[mess_key]["values"] = [value for value in date_json.values() if value > 0]

        # collect values for x - axis
        x_axis = [x for x in date_json.keys()]

        # collect values for y - axis
        y_axis = [y for y in date_json.values()]





        # minimum of all the values with corresponding year
        min_tuple = [(key, value) for key, value in date_json.items() if value == min(date_json.values())]

        median = np.median(y_axis)



        # maximum of all the values with corresponding year
        max_tuple = [(key, value) for key, value in date_json.items() if value == max(date_json.values())]

        dict[mess_key]["minimum"] = min_tuple[0][1]
        dict[mess_key]["minimum_year"] = min_tuple[0][0]


        dict[mess_key]["median"] = median



        dict[mess_key]["maximum"] = max_tuple[0][1]
        dict[mess_key]["maximum_year"] = max_tuple[0][0]








#save result in a file

with open(r"floodproject/historical_data/historical.json", "w") as file:
    json.dump(dict, file)


print(dict)

# x_plot = np.array(x_axis)
# y_plot = np.array(y_axis)
#
#
# plt.figure(figsize=(15,15))
# plt.plot(x_plot, y_plot)
# plt.xlabel("year")
# plt.xticks(rotation=20)
# plt.ylabel("water level in m³/s")
# plt.title("historical surface water levels")
# plt.show()