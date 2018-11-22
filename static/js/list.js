var rename_step_f_tmplt;
var rename_lesson_f_tmplt;
var rename_substep_tmplt_f_tmplt;
var isRecording = false;
const start_sound = new Audio("/static/sounds/start_sound.wav");
const stop_sound = new Audio("/static/sounds/stop_sound.wav");
const af_confirmation = new Audio("/static/sounds/af_confirmation.mp3");

function isInstanceName(value){
  return !(value == null || value === " " || value ==="  " || value === "" || value === undefined);
}

$(function  () {
    var context_tmplt_1 = [{name:"NoName"}];
    var compiledTemplate_1 = JST["static/extra/hb_templates/renameStep.handlebars"];
    rename_step_f_tmplt = compiledTemplate_1(context_tmplt_1);

    var context_tmplt_2 = [{name:"NoName"}];
    var compiledTemplate_2 = JST["static/extra/hb_templates/renameLesson.handlebars"];
    rename_lesson_f_tmplt = compiledTemplate_2(context_tmplt_2);

    var context_tmplt_3 = [{name:"NoName"}];
    var compiledTemplate_3 = JST["static/extra/hb_templates/renameSubstepTemplate.handlebars"];
    rename_substep_tmplt_f_tmplt = compiledTemplate_3(context_tmplt_3);
});

var cookie_csrf_updater = function(xhr){
    var cookie = null;
    var cookVal = null;
    var cookies = document.cookie.split(";");

    for (var i=0; i < cookies.length; i++) {
        cookie = jQuery.trim(cookies[i]);

        if(cookie.substring(0, "csrftoken".length+1) === "csrftoken=") {
            cookVal = decodeURIComponent(cookie.substring("csrftoken".length + 1));
            break;
        }
    }

    xhr.setRequestHeader("X-CSRFToken", cookVal)
};

    function upd_deleted_el(new_name, deleted_element) {
        if (new_name != null && new_name.length > 0) {
            var jq_deleted = $(deleted_element);
            var replace = $("<div/>").append(jq_deleted.clone());
            $(replace).find(".obj_name").html(new_name);
            deleted_element = replace.html();
        }
        return deleted_element;
    }

function record_started(callback) {
    $(".start_recording").removeClass("start_recording").addClass("stop_recording").text("Recording");
    var curr_sec_from_epoch = new Date().getTime() / 1000;
    $(".stop_recording").append('<div id = "timer" data-starttime='+curr_sec_from_epoch+'>00:00</div>');
    $(".tip-text").text("Click here or press the spacebar to stop");
    callback();
}

function record_start_failed(callback) {
    $(".start_recording").text("Start Recording");
    callback();
}

function record_stopped(callback) {
    $(".stop_recording").removeClass("stop_recording").addClass("start_recording").text("Start Recording");
    $(".tip-text").text("Click here or press the spacebar to start");
    callback();
}

var elements_subscriptor = function() {
    var deleted_element;

    function fader(el) {
        el.fadeTo("fast", .5).removeAttr("href");
    }

    $(".af_button").on("click", function (event) {
        if (isRecording) {
            return false;
        }

        const defaultColor = $(this).css("color");

        $(this).text("Processing...")
            .click(function () { return false; })
            .prop('disabled', true)
            .fadeTo("fast", .5)
            .css("color", "initial");

        const elem = $(this);

        var unlock = function(element) {
            element.text("Autofocus")
                .prop('disabled', false)
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
            elem.css("color", "red")
            setTimeout(function () {
                elem.css("color", defaultColor);
            }, 3000);
        });
    });

    function start_rec() {
        const elem = $(".start_recording");
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
                isRecording = true;
                start_sound.play();
                record_started(elements_subscriptor);

            },
            error: function (data) {
                $(window).off();
                alert(data.responseText);
                record_start_failed(elements_subscriptor);
            }
        });
    }

    $(window).on("beforeunload", function () {
         $(".start_recording").off();
    });

    function stop_rec() {
        const elem = $(".stop_recording");
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
                record_stopped(elements_subscriptor);
                isRecording = false;
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

    $(".start_recording").off().on("click", function(){
        start_rec();
    });

    $(".stop_recording").off().on("click", function(){
        stop_rec();
    });

    $("#edit-text").click(function() {
        $(".form-edit-text").toggleClass("hidden_form");
    });
};

const func_listener = function(){

    elements_subscriptor();

    setInterval(function() {
        var seconds = new Date().getTime() / 1000;
        var elem = $("#timer");
        elem.text(rectime(parseInt(seconds - elem.data("starttime"))));
    }, 1000); // 60 * 1000 milsec
   window.onunload=function(){void(0);}
};

$(document).ready(func_listener);

function rectime(sec) {
	var hr = Math.floor(sec / 3600);
	var min = Math.floor((sec - (hr * 3600))/60);
	sec -= ((hr * 3600) + (min * 60));
	sec += ""; min += "";
	while (min.length < 2) {min = "0" + min;}
	while (sec.length < 2) {sec = "0" + sec;}
	hr = (hr)?":"+hr:"";
	return hr + min + ":" + sec;
}


