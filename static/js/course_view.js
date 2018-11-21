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

//Shows modal dialog on rename button click
$(function () {
    $('a[href="#renameModalCenter"]').on("click", function () {
        const title = $(this).parent().parent().find(".lesson_name").text();
        $("#modalRenameTitle").text(title);
        $("#renameModalCenter").modal("show");
        // const urlink = $(this).data("urllink");
        // $("#modalDeleteButton").on("click", function () {
        //     window.location.replace(urlink);
        // });
    })
});