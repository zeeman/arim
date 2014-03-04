$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();
        submit_form();
    });

    $('a.edit').on('click', function(event) {
        event.preventDefault();
        device = load_device($(this).attr('data-id'));
    });
});


function set_errors(errors) {
    $.each(errors, function (name, text) {
        $('form').find('label[for=' + name + ']').first().after(
            '<span class="error">' + text + '</span>');
    });
}


function submit_form() {
    form = $('form');

    form.find('span.error').remove();
    $('#server-error').slideUp(200, 'easeInQuart');
    var post_data = form.find(':input').serializeArray();

    $.post(document.pathname, post_data, function(data) {
        location.reload();
    }, 'json').fail(function(data) {
        if (data.status == 422) {
            set_errors(data.responseJSON);
        } else {
            $('#server-error').slideDown(200, 'easeInQuart');
        };
    });
}


function load_device(id) {
    $('#server-error').slideUp(200, 'easeInQuart');

    $.get('/device?id=' + id, function(data) {
        $.each(data, function(name, value) {
            $('form').find('input[name=' + name + ']').val(value);
        });
    }, 'json').fail(function(data) {
        $('#server-error').slideDown(200, 'easeInQuart');
    });
}
