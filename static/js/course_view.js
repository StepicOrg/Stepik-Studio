//Adds form on dropdown show
$(function () {
    $(".add-item").on("show.bs.dropdown", function (e) {
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "GET",
            url: $(this).data("urllink"),
            success: function (data, status) {
                $("#add-form").append(data);
            }
        });
    });
});

//Removes form on dropdown hide
$(function () {
    $(".add-item").on("hide.bs.dropdown", function (e) {
        $("#add-form").empty();
    });
});

//Form validation updater
$(function () {
    $(document).on("submit", "#target", function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: $(".add-item").data("urllink"),
            data: $("#target").serialize(),
            success: function (data, status) {
                if (data === "Ok") {
                    location.reload(true);
                } else {
                    $("#add-form").empty().append(data);
                }
            }
        });
    });
});

//Doesn't close on menu click
$(function () {
    $(document).on("click", ".dropdown-menu", function (e) {
        e.stopPropagation();
    });
});

//Creates raw cut for whole lesson
$(function () {
    $(".raw_cut_lesson").on("click", function (event) {
        event.stopPropagation();
        $(this).text("Processing");
        const lesson_id = $(this).parents(".btn-group").attr("lessonID");
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: "/create-lesson-montage/" + lesson_id + "/",
            error: function (data) {
                alert(data.responseText);
            }
        });
    });
});

//Shows modal dialog on delete button click
$(function () {
    $('a[href="#deleteModalCenter"]').on("click", function () {
        const title = "Delete " + $(this).parent().parent().find(".lesson_name").text() + "?";
        $("#modalDeleteTitle").text(title);
        $("#deleteModalCenter").modal("show");
        const urlink = $(this).data("urllink");
        $("#modalDeleteButton").on("click", function () {
            window.location.replace(urlink);
        });
    })
});

//Focus on input field
$(function () {
    $('#renameModalCenter').on('shown.bs.modal', function () {
        $(this).find('[autofocus]').focus();
    });
});

//Clear error message on close
$(function () {
    $('#renameModalCenter').on('hidden.bs.modal', function (e) {
        $("#rename-error").empty();
    });
});

//Shows and handles modal dialog
$(function () {
    $('a[href="#renameModalCenter"]').on("click", function () {
        const lessonId = $(this).parents(".btn-group").attr("lessonID");
        const errorDesriptor = $("#rename-error");
        const title = $(this)
            .parent()
            .parent()
            .find(".lesson_name")
            .text();

        $("#lesson-new-name").focus(function () {
            errorDesriptor.empty();
        });

        $("#modalRenameTitle").text('Rename ' + '\'' + title + '\'');

        $("#renameModalCenter")
            .modal("show")
            .find('.modal-body input')
            .val(title);

        $("#modalRenameButton").on("click", function (e) {
            const sameNamesCount = $(".lesson_name").filter(function() {
                return ($(this).text() === $("#lesson-new-name").val());
            }).length;

            if (sameNamesCount !== 0) {
                errorDesriptor.text("Course already contains lesson with name " +
                    "\'" + $(this).text() + "\'");
                    return;
            }

            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "/rename-elem/",
                data: {
                    "id": lessonId,
                    "type": "lesson",
                    "name_new": $("#lesson-new-name").val()
                },
                success: function (data) {
                    window.location.reload();
                },
                error: function (request, status, errorThrown) {
                    errorDesriptor.text(request.responseText);
                }
            });
        });
    });
});
