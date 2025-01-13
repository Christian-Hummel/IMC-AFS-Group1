
function toggleTabs (target){

    const userprofile = document.getElementById("userprofile");
    const notifications = document.getElementById("notifications");
    const data = document.getElementById("data");

    const changepassword = document.getElementById("changepassword");
    const changelocation = document.getElementById("changelocation");


    // create a list of all tabs and iterate over it
    const array = [userprofile, notifications]

    array.forEach((element) => {
        if (target !== element.id){
            element.style.display = "none"
            // if condition to check if a button has got the class "active" - is highlighted
            if (document.getElementById(element.id.concat("button")).classList.contains("active")){
                document.getElementById(element.id.concat("button")).classList.remove("active")
            }
        }

    });

    if (target === "userprofile" && data.style.display === "none"){
        data.style.display = "block"
        changepassword.style.display = "none"
        changelocation.style.display = "none"
    }

    // make target div visible
    document.getElementById(target).style.display = "block";
    // highlight corresponding tab button
    document.getElementById(target.concat("button")).classList.add("active");


}

function toggleSubtabs(target) {

    data = document.getElementById("data");

    targetform = document.getElementById(target);

    if (targetform.style.display === "none") {
        targetform.style.display = "block"
        data.style.display = "none"
    } else {
        data.style.display = "block"
        targetform.style.display = "none"

    }

};

function markRead() {

    notifications = document.querySelectorAll('input:checked')

    notifications.forEach((element) => {

        var request = new XMLHttpRequest();

        readUrl = "/profile/setread/" + element.value

        request.open('GET', readUrl)

        request.send();

        if (element.parentNode.classList.contains("unread")) {
            element.parentNode.classList.remove("unread")
        }

    })


}

function markUnread() {

    notifications = document.querySelectorAll('input:checked')

    notifications.forEach((element) => {

        var request = new XMLHttpRequest();

        unreadUrl = "/profile/setunread/" + element.value

        request.open('GET', unreadUrl)

        request.send();

        if(!element.parentNode.classList.contains("unread")){
           element.parentNode.classList.add("unread")
        }

    })
}


function deleteNotification() {

    notifications = document.querySelectorAll('input:checked')

    notifications.forEach((element) => {

        var request = new XMLHttpRequest();

        deleteUrl = "/profile/deletenotif/" + element.value

        request.open('GET', deleteUrl)

        request.send();

        element.parentNode.parentNode.remove();

    })

    console.log(document.querySelectorAll('input[type=checkbox]'))

    if(document.querySelectorAll('input[type=checkbox]').length === 0){

        notifdiv = document.getElementById("notifications")
        markreadbutton = document.getElementById("markreadbutton")
        markunreadbutton = document.getElementById("markunreadbutton")
        notifdeletebutton = document.getElementById("notifdeletebutton")

        buttons = [markreadbutton, markunreadbutton, notifdeletebutton]

        buttons.forEach((element) =>{
            element.remove()
        })

        var paragraph = document.createElement("p")
        paragraph.textContent = "No Notifications at the moment"
        notifdiv.append(paragraph)

    }

}


