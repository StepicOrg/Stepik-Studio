//Adds form on dropdown show
$(function () {
    $(".add-item").on("show.bs.dropdown", function (e) {
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "GET",
            url: $(this).data("urllink"),
            success: function (data, status) {
                $("#add-form")
                    .append(data)
                    .find('[autofocus]')
                    .focus();
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

//Doesn't close dropdowns on click
$(function () {
    $(document).on("click", ".dropdown-menu", function (e) {
        e.stopPropagation();
    });
});

//Creates raw cut
$(function () {
    $(".raw_cut").on("click", function (event) {
        event.stopPropagation();
        $(this).text("Processing");
        const url = $(this).data("urllink");
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: url,
            error: function (data) {
                alert(data.responseText);
            }
        });
    });
});

//Shows modal dialog on delete button click
$(function () {
    $('a[href="#deleteModalCenter"]').on("click", function () {
        const title = "Delete " + $(this).parent().parent().find(".elem_name").text() + "?";
        $("#modalDeleteTitle").text(title);
        $("#deleteModalCenter").modal("show");
        const urlink = $(this).data("urllink");
        $("#modalDeleteButton").on("click", function () {
            window.location.replace(urlink);
        });
    })
});

//Focus on input field when rename modal opened
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

//Shows and handles rename modal dialog
$(function () {
    $('a[href="#renameModalCenter"]').on("click", function () {
        const elem_id = $(this).parents(".btn-group").attr("elem_id");
        const type = $(this).parents(".btn-group").find("a").attr("type");
        const errorDesriptor = $("#rename-error");
        const title = $(this)
            .parent()
            .parent()
            .find(".elem_name")
            .text();

        $("#new-name").focus(function () {
            errorDesriptor.empty();
        });

        $("#modalRenameTitle").text('Rename ' + '\'' + title + '\'');

        $("#renameModalCenter")
            .modal("show")
            .find('.modal-body input')
            .val(title);

        $("#modalRenameButton").on("click", function (e) {
            const sameNamesCount = $(".elem_name").filter(function() {
                return ($(this).text() === $("#new-name").val());
            }).length;

            if (sameNamesCount !== 0) {
                errorDesriptor.text("Element with name " +
                    "\'" + $("#new-name").val() + "\' already exists");
                    return;
            }

            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "/rename-elem/",
                data: {
                    "id": elem_id,
                    "type": type,
                    "name_new": $("#new-name").val()
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

//To make list elements draggable
$(function () {
    $(".sortable").sortable({
        axis: "y",
        distance: 15,
        stop: function (event, ui) {
            const type =$(ui.item[0]).find("a").attr("type");
            $.ajax({
                beforeSend: cookie_csrf_updater,

                type: "POST",
                url: "/reorder-lists/",

                data: {
                    "type": type,
                    "order": $(this).sortable("toArray"),
                    "ids": $(this).sortable("toArray",
                        {attribute: "elem_id"})
                },
            });
        }
    }).disableSelection();
});

//Enable tooltips
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});
