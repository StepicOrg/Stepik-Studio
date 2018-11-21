//Add form on dropdown show
$(function () {
    $(".add-item").on('show.bs.dropdown', function (e) {
        $.ajax({
            type: 'GET',
            url: '/add-lesson/',
            success: function (data, status) {
                $('#add-form').append(data);
            }
        });
    });
});

//Remove form on dropdown hide
$(function () {
    $(".add-item").on('hide.bs.dropdown', function () {
        $("#add-form").empty();
    });
});

//Form validation updater
$(function () {
    $(document).on('submit', "#target", function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: 'POST',
            url: '/add-lesson/',
            data: $("#target").serialize(),
            success: function (data, status) {
                if (data === 'Ok') {
                    location.reload(true);
                } else {
                    $('#add-form').empty().append(data);
                }
            }
        });
    });
});