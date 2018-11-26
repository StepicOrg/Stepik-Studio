//Locks substep
function lockSubstep(id) {
    const element = $(".substep-list[data-ss-id=" + id + "]");
    element.find("button")
        .each(function () {
            $(this).attr("disabled", "disabled");
        });

    element.find(".progress")
        .removeClass("d-none");
}

//Unlocks substep
function unlockSubstep(id) {
    const element = $(".substep-list[data-ss-id=" + id + "]");
    element.find("button")
        .each(function () {
            $(this).removeAttr("disabled");
        });

    element.find(".progress")
        .addClass("d-none");
}


$(function () {
    //Shows video content
    $(".show-content").click(function () {
        const title = $(this).parent().parent().find(".ss-name").text();
        const url = $(this).data("urllink");
        $("#modalVideoTitle").text(title);
        $(".video-content").append("<video controls preload='none' width='100%'>" +
            "<source class='video' src=" + url + ">" +
            "</video>");
        $("#videoModalCenter").modal("show");
        $("video").get(0).play();
    });

    //Makes video content empty on modal hide
    $("#videoModalCenter").on("hidden.bs.modal", function () {
        $("video").get(0).pause();
        $(".video-content").empty();
    });

    //Creates raw cut
    $(".create-raw-cut").on("click", function (event) {
        const redir_url = $(this).data("urllink");
        const ss_id = $(this).parent().parent().data("ss-id");

        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: redir_url,
            data: {
                "action": "start_montage"
            },
            success: function (data) {
                lockSubstep(ss_id);
            },
            error: function (data) {
                alert(data.responseText);
            }
        });
    });

    //Shows modal dialog on delete button click
    $(".delete-button").on("click", function () {
        const title = "Delete " + $(this).parent().parent().find(".ss-name").text() + "?";
        $("#modalDeleteTitle").text(title);
        $("#deleteModalCenter").modal("show");
        const urlink = $(this).data("urllink");
        $("#modalDeleteButton").on("click", function () {
            window.location.replace(urlink);
        });
    });

    //Statuses polling
    $(window).on("load", function (event) {
        var poller_id;
        $(this).on("unload", function () {
            clearInterval(poller_id);
        });

        const listIds = $(".substep-list")
            .map(function () {
                return $(this).data("ss-id");
            })
            .get();

        $(".substep-list").each(function () {
            if ($(this).data("ss-locked") === "False") {
                unlockSubstep($(this).data("ss-id"));
            }
        });

        poller_id = setInterval(function () {
            if (listIds.length === 0) {
                return false;
            }
            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "/substep-statuses/",
                dataType: "json",
                traditional: true,
                data: {"ids": listIds},
                success: function (data) {
                    $(".substep-list").each(function () {
                        const ss_id = $(this).data("ss-id");

                        //skip items which already deleted
                        if (!data[ss_id]) {
                            return true;
                        }
                        const elem = $(this);

                        if (data[ss_id].islocked) {
                            lockSubstep(ss_id);
                        } else if (data[ss_id].exists) {
                            unlockSubstep(ss_id);
                            elem.find(".create-raw-cut")
                                .addClass("d-none");
                            elem.find(".show-raw-cut")
                                .removeClass("d-none");
                        } else {
                            unlockSubstep(ss_id);
                            elem.find(".create-raw-cut")
                                .removeClass("d-none");
                            elem.find(".show-raw-cut")
                                .addClass("d-none");
                        }
                    });
                }
            });
        }, 1000);
    });

    //Save notes
    $(".save-notes").click(function () {
        const element = $(this);
        const urllink = element.data("urllink");
        const data = $("#form-notes").val();

        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: urllink,
            data: {"notes": data},
            success: function (data) {
                element.removeClass("btn-info")
                    .addClass("btn-success")
                    .text("Success");

                setTimeout(function () {
                    element.removeClass("btn-success")
                        .addClass("btn-info")
                        .text("Save");
                }, 1000);
            },
            error: function (data) {
                element.removeClass("btn-info")
                    .addClass("btn-danger")
                    .text("Error");

                setTimeout(function () {
                    element.removeClass("btn-danger")
                        .addClass("btn-info")
                        .text("Save");
                }, 1000);
            }
        });
    });

    //Handle autofocus button click
    $(".af_button").on("click", function (event) {
        const defaultColor = $(this).css("color");
        $(this).text("Processing...")
            .click(function () {
                return false;
            })
            .prop("disabled", true)
            .fadeTo("fast", 0.5)
            .css("color", "initial");

        const elem = $(this);

        var unlock = function (element) {
            element.text("Autofocus")
                .prop("disabled", false)
                .fadeTo("fast", 1);
        };

        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "GET",
            url: "/autofocus-camera/",
            timeout: 4000,

            success: function () {
                setTimeout(function () {
                    unlock(elem);
                    elem.css("color", "green");
                    af_confirmation.play();
                }, 1500);
            },
            error: function () {
                unlock(elem);
                elem.css("color", "red");
            },
        }).done(function () {
            setTimeout(function () {
                elem.css("color", defaultColor);
            }, 3000);
        }).fail(function () {
            elem.css("color", "red");
            setTimeout(function () {
                elem.css("color", defaultColor);
            }, 3000);
        });
    });
});