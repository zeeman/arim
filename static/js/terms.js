$(document).ready(function() {
    $('#agree1,#agree2').on('click', function() {
        $("button#submit").attr("disabled",
            !($('#agree1')[0].checked && $('#agree2')[0].checked));
    });


    $("button#submit").on('click', function(e) {
        e.preventDefault();
        if ($('#agree1')[0].checked && $('#agree2')[0].checked)) {
            location = '/devices';
        }
    });
});
