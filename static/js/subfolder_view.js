$(document).ready(function () {
    $(".add-item").on("show.bs.dropdown", function (e) { //Adds form on dropdown show
        $.ajax({
            beforeSend: getCookie,
            type: "GET",
            url: $(this).data("urllink"),
            success: function (data, status) {
                $("#add-form")
                    .append(data)
                    .find("[autofocus]")
                    .focus();
            }
        });
    }).on("hide.bs.dropdown", function (e) { //Removes form on dropdown hide
        $("#add-form").empty();
    });

    //Form validation updater
    $(document).on("submit", "#target", function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        $.ajax({
            beforeSend: getCookie,
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

    //Doesn't close dropdowns on click
    $(document).on("click", ".dropdown-menu", function (e) {
        e.stopPropagation();
    });

    //Creates raw cut
    $(".raw-cut").on("click", function (event) {
        event.stopPropagation();
        $(this).text("Processing");
        const url = $(this).data("urllink");
        $.ajax({
            beforeSend: getCookie,
            type: "POST",
            url: url,
            error: function (data) {
                alert(data.responseText);
            }
        });
    });

    //Shows modal dialog on delete button click
    $("a[href=\"#deleteModalCenter\"]").on("click", function () {
        const title = "Delete " + $(this).parent().parent().find(".elem-name").text() + "?";
        $("#modalDeleteTitle").text(title);
        $("#deleteModalCenter").modal("show")
                               .focus()
                               .keypress(function (e) {
                                   if (e.which === 13) {
                                       $("#modalDeleteButton").trigger("click");
                                   }
                               });

        const urlink = $(this).data("urllink");
        $("#modalDeleteButton").off().on("click", function () {
            window.location.replace(urlink);
        });
    });

    $("#renameModalCenter").on("shown.bs.modal", function () { //Focus on input field when rename modal opened
        $(this).find("[autofocus]")
               .focus();
    }).on("hidden.bs.modal", function (e) { //Clear error message on close
        $("#rename-error").empty();
    });

    //Shows and handles rename modal dialog
    $("a[href=\"#renameModalCenter\"]").on("click", function () {
        const elementTd = $(this).parents(".btn-group").attr("elem_id");
        const type = $(this).parents(".btn-group").find("a").attr("type");
        const errorDesriptor = $("#rename-error");
        const title = $(this)
            .parent()
            .parent()
            .find(".elem-name")
            .text();

        $("#new-name").off().focus(function () {
            errorDesriptor.empty();
        }).keypress(function (e) {
            if (e.which === 13) {
                $("#modalRenameButton").trigger("click");
            }
        });

        $("#modalRenameTitle").text("Rename " + "'" + title + "'");

        $("#renameModalCenter")
            .modal("show")
            .find(".modal-body input")
            .val(title);

        $("#modalRenameButton").off().on("click", function (e) {
            const sameNamesCount = $(".elem-name").filter(function () {
                return ($(this).text() === $("#new-name").val());
            }).length;

            if (sameNamesCount !== 0) {
                errorDesriptor.text("Element with name " +
                    "\'" + $("#new-name").val() + "\' already exists");
                return;
            }

            $.ajax({
                beforeSend: getCookie,
                type: "POST",
                url: "/rename-elem/",
                data: {
                    "id": elementTd,
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

    //To make list elements draggable
    $(".sortable").sortable({
        axis: "y",
        distance: 15,
        stop: function (event, ui) {
            const type = $(ui.item[0]).find("a").attr("type");
            $.ajax({
                beforeSend: getCookie,

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

    //Enable tooltips
    $("[data-toggle=\"tooltip\"]").tooltip()
});
