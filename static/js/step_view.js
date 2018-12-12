const afConfirmation = new Audio("/static/sounds/af_confirmation.mp3");

function deleteSubstepView(id) {
    const element = $(".substep-list[data-ss-id=" + id + "]");
    if (element) {
        element.remove();
    }
}

//Locks substep
function lockSubstep(id) {
    const element = $(".substep-list[data-ss-id=" + id + "]");
    element.data("ss-locked", "True")
           .find("button")
           .each(function () {
               if ($(this).hasClass("show-content")) {
                   return true;
               }
               $(this).attr("disabled", "disabled");
               $(this).tooltip("hide");
           });

    element.find(".progress")
           .removeClass("d-none");
}

//Unlocks substep
function unlockSubstep(id) {
    const element = $(".substep-list[data-ss-id=" + id + "]");
    element.data("ss-locked", "False")
           .find("button")
           .each(function () {
               $(this).removeAttr("disabled");
           });

    element.find(".progress")
           .addClass("d-none");
}

$(document).ready(function () {
    //Shows video content
    $(document).on("click", ".show-content", function () {
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
    $(document).on("click", ".create-raw-cut", function () {
        const redirectUrl = $(this).data("urllink");
        const substepId = $(this).parent().parent().data("ss-id");

        $.ajax({
            beforeSend: getCookie,
            type: "POST",
            url: redirectUrl,
            data: {
                "action": "start_montage"
            },
            success: function (data) {
                lockSubstep(substepId);
            },
            error: function (data) {
                alert(data.responseText);
            }
        });
    });

    //Shows modal dialog on delete button click
    $(document).on("click", ".delete-button", function () {
        const title = "Delete " + $(this).parent().parent().find(".ss-name").text() + "?";
        $("#modalDeleteTitle").text(title);
        $("#delete-error").empty();

        $("#deleteModalCenter").off()
                               .modal("show")
                               .focus()
                               .keypress(function (e) {
                                   if (e.which === 13) {
                                       $("#modalDeleteButton").trigger("click");
                                   }
                               });

        const urlink = $(this).data("urllink");
        const substepId = $(this).parent().parent().data("ss-id");

        $("#modalDeleteButton").off("click").on("click", function () {
            $.ajax({
                beforeSend: getCookie,
                type: "GET",
                url: urlink,
                success: function (data) {
                    deleteSubstepView(substepId);
                    $("#deleteModalCenter").modal("hide");
                },
                error: function (data) {
                    $("#delete-error").text(data.responseText);
                }
            });
        });
    });

    //Statuses polling
    $(window).on("load", function (event) {
        var pollerId;
        $(this).on("unload", function () {
            clearInterval(pollerId);
        });

        $(".substep-list").each(function () {
            if ($(this).data("ss-locked") === "False") {
                unlockSubstep($(this).data("ss-id"));
            }
        });

        pollerId = setInterval(function () {
            const listIds = $(".substep-list")
                .map(function () {
                    return $(this).data("ss-id");
                })
                .get();

            if (listIds.length === 0) {
                return false;
            }
            $.ajax({
                beforeSend: getCookie,
                type: "POST",
                url: "/substep-statuses/",
                dataType: "json",
                traditional: true,
                data: {"ids": listIds},
                success: function (data) {
                    $(".substep-list").each(function () {
                        const substepId = $(this).data("ss-id");

                        //skip items which already deleted
                        if (!data[substepId]) {
                            return true;
                        }
                        const elem = $(this);

                        if (data[substepId].islocked) {
                            lockSubstep(substepId);
                        } else if (data[substepId].exists) {
                            unlockSubstep(substepId);
                            elem.find(".create-raw-cut")
                                .addClass("d-none");
                            elem.find(".show-raw-cut")
                                .removeClass("d-none");
                        } else {
                            unlockSubstep(substepId);
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
            beforeSend: getCookie,
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
    $(".af-button").on("click", function (event) {
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
            beforeSend: getCookie,
            type: "GET",
            url: "/autofocus-camera/",
            timeout: 4000,

            success: function () {
                setTimeout(function () {
                    unlock(elem);
                    elem.css("color", "green");
                    afConfirmation.play();
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

    //Enable tooltips
    $("[data-toggle=\"tooltip\"]").tooltip()
});