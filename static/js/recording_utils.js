const startSound = new Audio("/static/sounds/start_sound.wav");
const stopSound = new Audio("/static/sounds/stop_sound.wav");

function recordStarted() {
    $(".start-recording")
        .removeClass("start-recording")
        .addClass("stop-recording")
        .removeAttr("disabled")
        .find(".head-text")
        .text("Recording");

    var currSecFromEpoch = new Date().getTime() / 1000;
    $(".stop-recording").append("<h1 id = \"timer\" data-starttime=" + currSecFromEpoch + ">00:00</h1>");
    $(".tip-text").text("Click here or press the spacebar to stop");
}

function recordStartFailed() {
    $(".start-recording")
        .removeAttr("disabled")
        .find(".head-text")
        .text("Start Recording");
}

function recordStopped() {
    $(".stop-recording")
        .removeClass("stop-recording")
        .addClass("start-recording")
        .removeAttr("disabled")
        .find(".head-text")
        .text("Start Recording");

    $("#timer").remove();
    $(".tip-text").text("Click here or press the spacebar to start");
}

$(document).ready(function () {
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

    $(document).on("click", ".start-recording", function (e) {
        $(".head-text").text("Starting...");
        $(".start-recording").attr("disabled", "disabled");

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
        $(".stop-recording").attr("disabled", "disabled");
        $(".head-text").text("Preparing...");
        $(".tip-text").empty();
        $("#timer").remove();

        $(window).off();
        $.ajax({
            beforeSend: getCookie,
            type: "GET",
            url: window.location.pathname + "stop/",
            success: function (data) {
                stopSound.play();
                recordStopped();
                $(".list-group").prepend(data);
                $("[data-toggle=\"tooltip\"]").tooltip();
            },
            error: function (data) {
                alert(data.responseText);
                location.reload(true);
            }
        });
    });

    setInterval(function () {
        var seconds = new Date().getTime() / 1000;
        var elem = $("#timer");
        elem.text(rectime(parseInt(seconds - elem.data("starttime"))));
    }, 1000);
});

