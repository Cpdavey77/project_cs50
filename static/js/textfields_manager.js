$(document).ready(function() {
    /*prevent login form submission when fields are empty*/
    $("#submit_login").click(function(){
        if ($(":text").val() == "" || $(":password").val() == "") {
            alert("Username/Password not entered")
            event.preventDefault();
        }
    })
    $("#submit").attr("disabled", "disabled");
    var title = $("#title");
    /*disable submit button when two forms are empty */
    $(".manager_form").keyup(function() {
        if ($("#description").val().length != 0  && $("#title").val().length != 0) {
            $("#submit").removeAttr("disabled");
        }
        else {
            $("#submit").attr("disabled", "disabled");
        }
    })
    /*prevent title and description in submitting*/
    $("#submit").click(function() {
        if ($(":text").val() == "" || $("textarea").val() == "") {
            alert("Title/Description cannot be empty")
            event.preventDefault();
        }
    })
    /*prevent submit in filing*/
    $("#submit_file").click(function() {
        if ($(":text").val() == ""  || $("textarea").val() == "" || $("input[type = 'number']").val() == ""){
            alert("Fields must be filled out")
            event.preventDefault();
        }
        else if ($("input[type = 'date']").val() == "") {
            alert("Please input date/s")
            event.preventDefault();
        }
    })
    /*prevent submit in feedback*/
    $(document).ready(function() {
        $("#submit_contact").click(function() {
            if ($("#feedback").val() == "") {
                alert("No feedback submitted. Try again")
                event.preventDefault();
            }
        })
    })
    /*tabs changing color*/
    $("[href]").each(function(){
        if (this.href == window.location.href) {
            $(this).addClass("active").css("color", "white");
        }
    })
})
