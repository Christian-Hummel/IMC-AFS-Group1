
var tempflag = false
// error if geolocation is not possible - does not check for denied permission, only the possibility
if (!navigator.geolocation) {
    throw new Error("No geolocation available");
}

// function to toggle stats for manager
function showVotestats(){
    var x = document.getElementById("votestats")
    if (x.style.display === "none"){
        x.style.display = "block";
    } else {
        x.style.display = "none"
    }
}

function toggleSubscribe(){
    var request = new XMLHttpRequest();

    request.open('GET', subscribeUrl);

    request.send();

    setTimeout(() => {
        window.location.reload();
    }, 10)

}

function toggleTabs() {
    const details = document.getElementById("details")
    const comments = document.getElementById("comments")

    const dbutton = document.getElementById("detailsbutton")
    const cbutton = document.getElementById("commentsbutton")

    if (details.style.display === "none"){
        details.style.display = "block";
        comments.style.display = "none";

        dbutton.classList.add("active")
        cbutton.classList.remove("active")

    } else if (comments.style.display === "none"){
        comments.style.display = "block";
        details.style.display = "none";

        cbutton.classList.add("active")
        dbutton.classList.remove("active")

    }
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

        // call for user id
    const user_id = JSON.parse(document.getElementById('user_id').textContent);

    // call for role of a user if needed
    const user_role = JSON.parse(document.getElementById('user_role').textContent);


    // extract user id
    if (user_id){
       console.log("user_id", user_id);
       console.log("user_role", user_role);
    }

    // if condition to add html tags if the distance is lower than value x - 25 kilometers for this example
    if (dist < 25 && user_id) {

        //repdetails = document.getElementById("report-container")


        // access reportvote form
        reportvote = document.getElementById("reportvote")

        // access severity rating
        severityselect = document.getElementById("severityselect")
        // checkbox - for credibility
        checkbox = document.getElementById("invcheck")
        // label of checkbox
        checklabel = document.getElementById("checklabel")
        // submit button
        vsubmit = document.getElementById("vsubmit")

        // change status of severity select tag
        severityselect.removeAttribute("hidden")
        // change status from checkbox - hidden input tag
        checkbox.setAttribute("type", "checkbox")
        // add text via javascript
        checklabel.outerHTML += "Mark inappropriate"
        // change status of submit button
        vsubmit.removeAttribute("hidden")

    }







}

jQuery(document).on('submit', '#submitcomment', function(e){
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: submitUrl,
            data: {
                textcomment: $('#textcomment').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                // extract raw value from hidden input field - comments.val() to extract value as string
                var comments = $("#ccount");

                var userId = JSON.parse(document.getElementById('user_id').textContent)
                var subscriptions = JSON.parse(document.getElementById('subscriptions').textContent)

                var unsubscribe = document.getElementById("unsubscribe")
                var subscribe = document.getElementById("subscribe")

                if (subscriptions.indexOf(userId) < 0 && tempflag === false){

                    console.log("not subscribed")


                    var request = new XMLHttpRequest();

                    request.open('GET', subscribeUrl);

                    request.send();

                    unsubscribe.style.display = ""
                    subscribe.style.display = "none"

                    tempflag = true




                } else {
                    console.log("subscribed")
                }

                // if there are no comments yet
                if (Number(comments.val()) === 0){
                    // add comment to the end of div with id comments
                    $('.comments').append(data);

                    //increment value -> +1

                    comments.val(parseInt(comments.val()+1));

                    // remove error message from the document
                    var commenterror = document.getElementById("comment-error")
                    commenterror.style.display = "none"

                    // if there are already comments, increment hidden input value and add comment as first element
                } else {
                    $('.comments').find('.comment').first().prepend(data);
                    comments.val( parseInt(comments.val())+1);
                }
                $("#textcomment").val('');
            }

        })
})



