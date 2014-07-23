$(document).ready(function() {
    $('form').on('submit', function(event) {
        event.preventDefault();
        submit_form();
    });

    $('a.edit').on('click', function(event) {
        event.preventDefault();
        device = load_device($(this).closest('tr').attr('data-id'));
    });

    $('a.delete').on('click', function(event) {
        event.preventDefault();
        confirm_delete_device($(this).closest('tr').attr('data-id'));
    });

    $('button#prefill-mac').on('click', function(event) {
        $('form#device-form').find('input#mac').val(
            $(this).attr('data-mac')
        );
    });

    $('button#reset-form').on('click', function(event) {
        reset_form();
    });
});


function set_form_errors(errors) {
    $.each(errors, function (name, text) {
        $('form').find('label[for=' + name + ']').first().after(
            '<span class="error">' + text + '</span>');
    });
}


function clear_form_errors() {
    $('form').find('span.error').remove();
    $('#form-error').slideUp(200, 'easeInQuart');
}


function reset_form() {
    clear_form_errors();
    $('input[name=id]').val('');
    $('#form-title').html('Register a new device');
    $('button[type=submit]').html('Register');
}


function submit_form() {
    var form = $('form');
    var form_error = $('#form-error');

    clear_form_errors();

    var post_data = form.find(':input').serializeArray();

    var id = $('input#id').val();
    var mac = $('input#mac').val();
    function is_duplicate() {
        return $(this).find('td.device-mac').html() == mac
            && $(this).attr('data-id') != id;
    }
    var conflict = $('tr[data-id]').filter(is_duplicate).length != 0;
    if (conflict) {
        form_error.html(
            "You've already registered a device with this MAC address.");
        form_error.slideDown(200, 'easeInQuart');
        return;
    }

    post_data['csrfmiddlewaretoken'] =
        $('#metadata').attr('data-csrfmiddlewaretoken');

    $('button#reset-form').css('display', 'none');
    $('img#loading').css('display', 'inline');
    $.post(document.pathname, post_data, function(data) {
        location.reload();
    }, 'json').fail(function(data) {
        $('button#reset-form').css('display', 'inline-block');
        $('img#loading').css('display', 'none');
        if (data.status == 422) {
            set_form_errors(data.responseJSON);
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


function clear_device_list_errors() {
    $('#device-list-server-error').slideUp(200, 'easeInQuart');
}


function load_device(id) {
    clear_form_errors();
    clear_device_list_errors();

    $('#form-title').html('Modify a device');
    $('button[type=submit]').html('Modify');

    // the data is already on the page, so we pull it from there
    tr = get_tr(id);
    $('form#device-form').find('input#id').val(tr.attr('data-id'));
    $('form#device-form').find('input#description').val(tr.find('td.device-description').text());
    $('form#device-form').find('input#mac').val(tr.find('td.device-mac').text());
}


function confirm_delete_device(id) {
    clear_device_list_errors();

    btn = $('button#deleteDevice');
    btn.attr('data-id', id);
    btn.on('click', function(event) {
        event.preventDefault();
        $('img#loadingDelete').css('display', 'inline');
        delete_device($(this).attr('data-id'));

        if ($('input#id').val() == id) {
            $('input#id').val('');
            $('#form-title').html('Register a new device');
            $('button[type=submit]').html('Register');
        }
    });

    $("#deleteDeviceModal").modal();
}


function delete_device(id) {
    clear_device_list_errors();

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
        $('img#loadingDelete').css('display', 'none');
    }).fail(function() {
        $('img#loadingDelete').css('display', 'none');
        $('#device-list-server-error').slideDown(200, 'easeInQuart');
    });
    $("#deleteDeviceModal").modal('hide');
    location.reload();
}
