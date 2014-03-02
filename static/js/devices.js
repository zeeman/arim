$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();
        ajax_form_submit(this);
    });
});


function set_errors(form, errors) {
    $.each(errors, function (name, text) {
        $(form).find('label[for=' + name + ']').first().after(
            '<span class="error">' + text + '</span>');
    });
}


function ajax_form_submit(form) {
    $(form).find('span.error').remove();
    $('#server-error').slideUp(200, 'easeInQuart');
    var post_data = $(form).find(':input').serializeArray();

    $.post(form.target, post_data, function(data) {
        window.reload();
    }, 'json').fail(function(data) {
        if (data.status == 422) {
            set_errors(form, data.responseJSON);
        } else {
            $('#server-error').slideDown(200, 'easeInQuart');
        };
    });
}
