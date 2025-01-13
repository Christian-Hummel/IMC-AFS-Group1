
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
    console.log("b")
}


// jQuery(document).on('submit', '#submitchanges', function(e){
//         e.preventDefault();
//         $.ajax({
//             type: 'POST',
//             url: submitUrl,
//             data: {
//                 textcomment: $('#textcomment').val(),
//                 csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
//             },
//             success: function (data) {
//                 // extract raw value from hidden input field - comments.val() to extract value as string
//                 var comments = $("#ccount");
//
//                 var userId = JSON.parse(document.getElementById('user_id').textContent)
//                 var subscriptions = JSON.parse(document.getElementById('subscriptions').textContent)
//
//                 var unsubscribe = document.getElementById("unsubscribe")
//                 var subscribe = document.getElementById("subscribe")
//
//                 if (subscriptions.indexOf(userId) < 0 && tempflag === false){
//
//
//                     var request = new XMLHttpRequest();
//
//                     request.open('GET', subscribeUrl);
//
//                     request.send();
//
//                     unsubscribe.style.display = ""
//                     subscribe.style.display = "none"
//
//                     tempflag = true
//
//                 }
//
//                 // if there are no comments yet
//                 if (Number(comments.val()) === 0){
//                     // add comment to the end of div with id comments
//                     $('.comments').append(data);
//
//                     //increment value -> +1
//
//                     comments.val(parseInt(comments.val()+1));
//
//                     // remove error message from the document
//                     var commenterror = document.getElementById("comment-error")
//                     commenterror.style.display = "none"
//
//                     // if there are already comments, increment hidden input value and add comment as first element
//                 } else {
//                     $('.comments').find('.comment').first().prepend(data);
//                     comments.val( parseInt(comments.val())+1);
//                 }
//                 $("#textcomment").val('');
//             }
//
//         })
// })

// min-height: 100vh;

//