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

//Shows video content
$(function () {
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
});

//Makes video content empty on modal hide
$(function () {
    $("#videoModalCenter").on('hidden.bs.modal', function () {
        $("video").get(0).pause();
        $(".video-content").empty();
    });
});

//Creates raw cut
$(function () {
    $(".create-raw-cut").on("click", function (event) {
        const elem = $(this);
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
});

//Shows modal dialog on delete button click
$(function () {
    $(".delete-button").on("click", function () {
        const title = "Delete " + $(this).parent().parent().find(".ss-name").text() + "?";
        $("#modalDeleteTitle").text(title);
        $("#deleteModalCenter").modal("show");
        const urlink = $(this).data("urllink");
        $("#modalDeleteButton").on("click", function () {
            window.location.replace(urlink);
        });
    })
});

//Statuses polling
$(function () {
    $(window).on("load", function (event) {
        var poller_id;
        $(this).on("unload", function () {
            clearInterval(poller_id);
        });

        const list = $(".substep-list")
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
            if (list.length === 0) {
                return false;
            }
            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "/substep-statuses/",
                dataType: "json",
                traditional: true,
                data: {'ids': list},
                success: function (data) {
                    $(".substep-list").each(function () {
                        const ss_id = $(this).data("ss-id");
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
});

// $(function () {
//     $(document).keyup(function (event) {
//
//         const elem = $(".modal[aria-hidden='False']");
//         console.info(elem.html());
//
//         if (elem) { //to disable handler when dialog is open
//             return false;
//         } else {
//             console.info('adsf');
//         }
//
//         if (event.target.type === "text" || event.target.type === "textarea") {
//             return false;
//         }
//
//         event.stopImmediatePropagation();
//         if (event.which === 32) {
//             if (!isRecording)
//                 $(".start_recording").trigger("click");
//             else
//                 $(".stop_recording").trigger("click");
//         }
//     });
// });