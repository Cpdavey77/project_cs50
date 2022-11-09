$(document).ready(function() {
    $(".table tbody tr").each(function(){
        $(".table tbody tr td").each(function() {
            var status = $(this);
            if (status.html() == "Pending") {
                status.css("color", "orange");
            }
            else if (status.html() == "Approved") {
                status.css("color", "green");
            }
            else if (status.html() == "Rejected") {
                status.css("color", "red");
            }
        })
    })
})