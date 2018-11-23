const start_sound = new Audio("/static/sounds/start_sound.wav");
const stop_sound = new Audio("/static/sounds/stop_sound.wav");
const af_confirmation = new Audio("/static/sounds/af_confirmation.mp3");

function recordStarted(callback) {
    $(".start-recording").removeClass("start-recording").addClass("stop-recording").text("Recording");
    var curr_sec_from_epoch = new Date().getTime() / 1000;
    $(".stop-recording").append('<div id = "timer" data-starttime=' + curr_sec_from_epoch + '>00:00</div>');
    $(".tip-text").text("Click here or press the spacebar to stop");
    callback();
}

function recordStartFailed(callback) {
    $(".start-recording").text("Start Recording");
    callback();
}

function recordStopped(callback) {
    $(".stop-recording").removeClass("stop-recording").addClass("start-recording").text("Start Recording");
    $(".tip-text").text("Click here or press the spacebar to start");
    callback();
}

//Start & stop on spacebar click
$(function () {
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
    });
});

var elements_subscriptor = function () {
    function start_rec() {
        const elem = $(".start-recording");
        elem.text("Starting...").click(function () {
            setTimeout(fader, 0, elem);
            return false;
        });
        elem.off();

        $(window).on("beforeunload", function () {
            return "Are you sure want to leave page? Recording will stop on leave.";
        });

        $(window).on("unload", function () {
            navigator.sendBeacon("/stop-recording/");
        });

        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: window.location.pathname,
            data: {
                "action": "start"
            },
            success: function () {
                start_sound.play();
                recordStarted(elements_subscriptor);

            },
            error: function (data) {
                $(window).off();
                alert(data.responseText);
                recordStartFailed(elements_subscriptor);
            }
        });
    }

    $(window).on("beforeunload", function () {
        $(".start-recording").off();
    });

    function stop_rec() {
        const elem = $(".stop-recording");
        elem.text("Preparing...").click(function () {
            return false;
        });
        elem.off();
        $(window).off();
        $.ajax({
            beforeSend: function (jqXHR) {
                cookie_csrf_updater(jqXHR);
                setTimeout(fader, 0, elem);
            },
            type: "POST",
            url: window.location.pathname,
            data: {
                "action": "stop"
            },
            success: function () {
                stop_sound.play();
                recordStopped(elements_subscriptor);
                location.reload(true);
            },
            error: function (data) {
                alert(data.responseText);
                location.reload(true);
            }
        });
    }

    $(document).keypress(function (event) {
        if (event.which === 32 && event.target.type !== "text" && event.target.type !== "textarea") {
            event.preventDefault();
        }
    });

    $(".start-recording").off().on("click", function () {
        start_rec();
    });

    $(".stop-recording").off().on("click", function () {
        stop_rec();
    });
};

const func_listener = function () {
    elements_subscriptor();
    setInterval(function () {
        var seconds = new Date().getTime() / 1000;
        var elem = $("#timer");
        elem.text(rectime(parseInt(seconds - elem.data("starttime"))));
    }, 1000); // 60 * 1000 milsec
    window.onunload = function () {
        void(0);
    }
};

$(document).ready(func_listener);


