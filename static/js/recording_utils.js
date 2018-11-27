const startSound = new Audio("/static/sounds/start_sound.wav");
const stopSound = new Audio("/static/sounds/stop_sound.wav");

function recordStarted() {
    $(".start-recording").removeClass("start-recording")
        .addClass("stop-recording")
        .find(".head-text")
        .text("Recording");

    var currSecFromEpoch = new Date().getTime() / 1000;
    $(".stop-recording").append("<div id = \"timer\" data-starttime=" + currSecFromEpoch + ">00:00</div>");
    $(".tip-text").text("Click here or press the spacebar to stop");
}

function recordStartFailed() {
    $(".start-recording").find(".head-text").text("Start Recording");
}

function recordStopped() {
    $(".stop-recording")
        .removeClass("stop-recording")
        .addClass("start-recording")
        .find(".head-text")
        .text("Start Recording");

    $("#timer").remove();
    $(".tip-text").text("Click here or press the spacebar to start");
}

$(function () {
    //Start & stop on spacebar click
    $(document).keyup(function (event) {
        if (event.target.type === "text" || event.target.type === "textarea") {
            return false;
        }
        if (event.which === 32) {
            const shownModalsCount = $(document).find(".modal").filter(function () {
                const element = $(this);
                return (element.data("bs.modal") || {})._isShown
            }).length;
            if (shownModalsCount !== 0) {
                return;
            }
            //fires only for one which is existing
            $(".start-recording").trigger("click");
            $(".stop-recording").trigger("click");
        }
    }).keypress(function (event) {
        if (event.which === 32 && event.target.type !== "text" && event.target.type !== "textarea") {
            event.preventDefault();
        }
    });

    $(window).on("beforeunload", function () {
        $(".start-recording").off();
    });

    $(".start-recording").on("click", function () {
        $(this).find(".head-text")
            .text("Starting...")
            .click(function () {
                return false;
            });

        $(this).off();

        $(window).on("beforeunload", function () {
            return "Are you sure want to leave page? Recording will stop on leave.";
        }).on("unload", function () {
            navigator.sendBeacon("/stop-recording/");
        });

        $.ajax({
            beforeSend: getCookie,
            type: "POST",
            url: window.location.pathname,
            data: {
                "action": "start"
            },
            success: function () {
                startSound.play();
                recordStarted();
            },
            error: function (data) {
                $(window).off();
                alert(data.responseText);
                recordStartFailed();
            }
        });
    });

    $(document).on("click", ".stop-recording", function () {

        $(this).click(function () {
            return false;
        });

        $(".head-text").text("Preparing...");
        $(".tip-text").empty();
        $(this).find("#timer").empty();
        $(this).off();

        $(window).off();
        $.ajax({
            beforeSend: getCookie,
            type: "POST",
            url: window.location.pathname,
            data: {
                "action": "stop"
            },
            success: function () {
                stopSound.play();
                location.reload(true);
                recordStopped();
            },
            error: function (data) {
                alert(data.responseText);
                location.reload(true);
            }
        });
    });

    $(document).ready(function () {
        setInterval(function () {
            var seconds = new Date().getTime() / 1000;
            var elem = $("#timer");
            elem.text(rectime(parseInt(seconds - elem.data("starttime"))));
        }, 1000);
    });
});

