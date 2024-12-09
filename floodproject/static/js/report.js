

// error if geolocation is not possible - does not check for denied permission, only the possibility
if (!navigator.geolocation) {
    throw new Error("No geolocation available");
}


// function to calculate distance between two coordinates - straight line
function distance(lst1, lst2){
    var R = 3958.8; // Radius of the Earth in miles
    var rlat1 = lst1[0] * (Math.PI/180); // Convert degrees to radians
    var rlat2 = lst2[0] * (Math.PI/180); // Convert degrees to radians
    var difflat = rlat2-rlat1; // Radian difference (latitudes)
    var difflon = (lst2[1]-lst1[1]) * (Math.PI/180); // Radian difference (longitudes)

    var d = (2 * R * Math.asin(Math.sqrt(Math.sin(difflat/2)*Math.sin(difflat/2)+Math.cos(rlat1)*Math.cos(rlat2)*Math.sin(difflon/2)*Math.sin(difflon/2))))* 1.60934;
    return d;
}


window.navigator.geolocation.getCurrentPosition(
  position => {
    const location = {
      lat:position.coords.latitude,
      long:position.coords.longitude
    }
    computeDistance(location); // <- Function that will use location data
  }, // error popup if permission for GPS data is denied by user
  (err)=> alert("Please allow the application to access your location")


);
function computeDistance(location) {
    console.log("location call", location);


    // extract coordinates from current location
    const clat = location.lat;
    const clon = location.long;

    const loclist = [clat,clon]

    // access coordinates from reportdetails.html
    const longitude = document.getElementById("longitude").textContent
    const latitude = document.getElementById("latitude").textContent

    const reportlist = [latitude, longitude]

    // calculate distance between current and report location - km
    var dist = distance(reportlist, loclist)

    console.log("distance in kilometers", dist)


    // if condition to add html tags if the distance is lower than value x - 80 kilometers for this example
    if (dist < 80) {

        repdetails = document.getElementById("report-container")

        repdetails.innerHTML += "<button>Submit Rating</button>"

        console.log(repdetails)
    }




}


