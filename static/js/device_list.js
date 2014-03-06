$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();
        submit_form();
    });

    $('a.edit').on('click', function(event) {
        event.preventDefault();
        device = load_device($(this).attr('data-id'));
    });

    $('a.delete').on('click', function(event) {
        event.preventDefault();
        delete_device($(this).attr('data-id'));
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
    $('#form-server-error').slideUp(200, 'easeInQuart');
    var post_data = form.find(':input').serializeArray();
    post_data['csrfmiddlewaretoken'] =
        $('#metadata').attr('data-csrfmiddlewaretoken');

    $('img#loading').css('display', 'inline');
    $.post(document.pathname, post_data, function(data) {
        $('img#loading').css('display', 'none');
        location.reload();
    }, 'json').fail(function(data) {
        $('img#loading').css('display', 'none');
        if (data.status == 422) {
            set_errors(data.responseJSON);
        } else {
            $('#form-server-error').slideDown(200, 'easeInQuart');
        };
    });
}


function load_device(id) {
    $('#device-list-server-error').slideUp(200, 'easeInQuart');

    $('#form-title').html('Change a device');

    $.get('/device?id=' + id, function(data) {
        $.each(data, function(name, value) {
            $('form').find('input[name=' + name + ']').val(value);
        });
    }, 'json').fail(function() {
        $('#device-list-server-error').slideDown(200, 'easeInQuart');
    });
}


function delete_device(id) {
    $('#device-list-server-error').slideUp(200, 'easeInQuart');

    post_data = {
        'id': id,
        'csrfmiddlewaretoken': $('#metadata').attr('data-csrfmiddlewaretoken')
    };

    $.post('/delete_device', post_data, function(data) {
        location.reload();
    }).fail(function() {
        $('#device-list-server-error').slideDown(200, 'easeInQuart');
    });
}
