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
        confirm_delete_device($(this).attr('data-id'));
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
    form_error = $('#form-error');
    form_error.slideUp(200, 'easeInQuart');

    var post_data = form.find(':input').serializeArray();
    post_data['csrfmiddlewaretoken'] =
        $('#metadata').attr('data-csrfmiddlewaretoken');

    $('img#loading').css('display', 'inline');
    $.post(document.pathname, post_data, function(data) {
        location.reload();
    }, 'json').fail(function(data) {
        $('img#loading').css('display', 'none');
        if (data.status == 422) {
            set_errors(data.responseJSON);
        } else {
            form_error.html('A server error occurred.');
            form_error.slideDown(200, 'easeInQuart');
        };
    });
}

// helper function to get reference to a given device's table row
function get_tr(id) {
    return $("tr[data-id=" + id + "]");
}

function load_device(id) {
    $('#form-error').slideUp(200, 'easeInQuart');
    $('#device-list-server-error').slideUp(200, 'easeInQuart');
    $(':input').attr('disabled', false);

    $('#form-title').html('Change a device');

    // the data is already on the page, so we pull it from there
    tr = get_tr(id);
    $('form#device-form').find('input#id').val(tr.find('a.edit').attr('data-id'));
    $('form#device-form').find('input#description').val(tr.find('td.device-description').text());
    $('form#device-form').find('input#mac').val(tr.find('td.device-mac').text());
}


function confirm_delete_device(id) {
    btn = $('button#deleteDevice');

    btn.attr('data-id', id);

    btn.on('click', function(event) {
        event.preventDefault();
        $('img#loadingDelete').css('display', 'inline');
        delete_device($(this).attr('data-id'));
    });
    $("#deleteDeviceModal").modal();
}


function delete_device(id) {
    $('#device-list-server-error').slideUp(200, 'easeInQuart');

    post_data = {
        'id': id,
        'csrfmiddlewaretoken': $('#metadata').attr('data-csrfmiddlewaretoken')
    };

    $.post('/delete_device', post_data, function(data) {
        //location.reload();
        tr = get_tr(id);
        tr.fadeOut(200, function(){ tr.remove(); });
        num_span = $('span#number-of-devices');
        num_span.text(parseInt(num_span.text()) - 1);
    }).fail(function() {
        $('img#loadingDelete').css('display', 'none');
        $('#device-list-server-error').slideDown(200, 'easeInQuart');
    });
    $("#deleteDeviceModal").modal('hide');
}
