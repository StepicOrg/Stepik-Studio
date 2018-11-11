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

function show_video_popup(ref, elem, width=1080, height=720) {
    elem.append("<div class='modal video_popup'><video controls preload='none' width='100%' height='100%'>" +
                    "<source class='video' src=" + ref + ">" +
                    "</video></div>");
    elem.find(".modal").dialog({
        resizable: false,
        draggable: false,
        modal: true,
        height: height,
        width: width,
        position: {
            my: "center",
            at: "top",
            of: window
        },
        open: function () {
            $("video").get(0).play();
            $('.ui-widget-overlay').bind('click', function () {
                $(".modal").dialog('close');
            });
        },
        close: function () {
            $("video").remove();
            $(".modal").remove();
        },
    });
}

var elements_subscriptor = function() {
    sortObj = $("#sortable");

    sortObj.sortable({
        start: function(e, ui) {
            if (!$("#isDraggable").is(":checked")) {
                window.location = $(ui.item[0]).find("a").attr("href");
            }
        },
        stop : function(event, ui) {
            var reorderingSteps = $(ui.item[0]).find("a").hasClass("step_name");
            var reorderingType = reorderingSteps ? "step" : "lesson";
            $.ajax({
                beforeSend: cookie_csrf_updater,

                type: "POST",
                url: "/reorder-lists/",

                data: {"type": reorderingType, "order": $(this).sortable("toArray"), "ids": $(this).sortable("toArray",
                    {attribute: reorderingSteps ? "stepID" : "lessonID"})},
                success: function(data){
                        //alert(data);
                }
            });
        }

    });

    sortObj.disableSelection();

    var deleted_element;

    $(".rename_button").off().on("click", function(e) {
        e.stopPropagation();
        var name = $(this).parents(".ui-state-default").find(".obj_name").text();
        $(this).fadeOut("fast",  function(){
            if ($(this).hasClass("step_rename")) {
                deleted_element = $(this).parent().parent().html();
                $(this).parent().parent().html(rename_step_f_tmplt);
            }
            else if ($(this).hasClass("lesson_rename")) {
                deleted_element = $(this).parent().parent().html();
                $(this).parent().parent().html(rename_lesson_f_tmplt);
            } else if ($(this).hasClass("substep_tmpl_rename")) {
                deleted_element = $(this).parent().html();
                $(this).parent().html(rename_substep_tmplt_f_tmplt);
            }
            else {
                alert("TEMPLATE ERROR!");
            }
            elements_subscriptor();
            $("#input_field_name").val(name);
            });
        });

    $("#cancel-rename").off().live("click", function(event, new_name) {
        $(this).fadeOut("fast",  function(){
            deleted_element = upd_deleted_el(new_name, deleted_element);
            console.log("deleted_element:" , deleted_element);
            console.log("new_element:", new_name);
            $(this).parents(".input_step_name_field").html(deleted_element);
            $(this).parents(".input_lesson_name_field").html(deleted_element);
            $(this).parents(".rename-substep-template-field").html(deleted_element);
            elements_subscriptor();
        });
    });


    $(".lesson_info").off().on("click", function() {
        $(this).parent().find(".lesson_path").toggleClass("hidden_info");
        $(this).parent().find(".lesson_info_link").toggleClass("hidden_info");
        $(this).parent().find("a").toggleClass("hidden_info");
    });

    $(".delete_button").on("click", function(event) {
        event.stopImmediatePropagation();

        if (isRecording) {
            alert("Please stop recording before");
            return false;
        }

        var redir_url = $(this).find(".delete-url").data("urllink");
        var _ss_name = $(this).parents(".substep_list").find(".substep_name").text().split(/ /)[0];
        var _s_name = $(this).parents(".ui-state-default").find(".step_name").text();
        var _name = undefined;
        if (isInstanceName(_s_name)){
            _name = _s_name;
        } else if (isInstanceName(_ss_name)) {
            _name = _ss_name;
        }
        $(this).append("<div class='modal'> Action can't be undone. Are you sure?</div>");
        $(this).find(".modal").dialog({
            resizable: false,
            modal: true,
            title: _name,
            height: 250,
            width: 400,
            position: {
                my: "center",
                at: "top",
                of: window
            },
            buttons: {
                    "Yes": function () {
                        $(this).dialog("close");
                        window.location.replace(redir_url);
                    },
                    "No": function () {
                        $(this).dialog("close");
                    }
            },
            close: function () {
                $(".modal").remove();
            },
        });
    });

    $(".show_content").on("click", function (event) {
        event.stopPropagation();
        const ss_id = $(this).data("ss_id");
        show_video_popup("/showcontent/" + ss_id +"/", $(this));
    });

    $(".show_screen_content").on("click", function (event) {
        event.stopPropagation();
        const ss_id = $(this).data("ss_id");
        show_video_popup("/showscreencontent/" + ss_id +"/", $(this));
    });

    $(".show_montage").on("click", function (event) {
        event.stopPropagation();
        const ss_id = $(this).data("ss_id");
        show_video_popup("/show-montage/" + ss_id +"/", $(this), width=1800, height=600);
    });

    function fader(el) {
        el.fadeTo("fast", .5).removeAttr("href");
    }

    $(".raw_cut_step").on("click", function(event) {
        event.stopPropagation();
        $(this).text("Processing");
        var step_id = $(this).parents(".ui-state-default").attr("stepID");
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: "/create-step-montage/" + step_id + "/",

            data: {
                "action": "create_step_montage"
            },
            error: function(data){
                alert(data.responseText);
            }
        });
    });

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
            }
        });
    }

    $(".raw_cut_lesson").on("click", function(event){
        event.stopPropagation();
        $(this).text("Processing");
        const lesson_id = $(this).parents(".ui-state-default").attr("lessonID");
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: "/create-lesson-montage/" + lesson_id + "/",
            error: function(data){
                alert(data.responseText);
            }
        });
    });

    $(".start_montage").on("click", function(event){
        event.stopPropagation();
        $(this).hide();
        const elem = $(this);
        const redir_url = $(this).data("urllink");
        const ss_id = $(this).data("ss_id");
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: redir_url,
            data: {
                "action": "start_montage"
            },
            success: function(data){
                $(".substep_list").each(function() {
                    if ($(this).data("ss_id") === ss_id) {
                        $(this).css("background", "#141628")
                            .css("pointer-events", "none")
                            .css("cursor", "default")
                            .data("ss_locked", "True");
                        $(this).children(".show_montage").show();
                    }
                });
            },
            error: function(data){
                alert(data.responseText);
                elem.show();
            }
        });
    });

    $(window).on("load", function(event) {
        var poller_id;
       $(this).on("unload", function() {
            clearInterval(poller_id);
            event.preventDefault();
            list.empty();
        });
        const list = $(".substep_list")
            .map(function () {
                return $(this).data("ss_id");
            })
            .get();

        poller_id = setInterval(function() {
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
                    $(".substep_list").each(function () {
                        const ss_id = $(this).data("ss_id");
                        const elem = $(this);
                        const show_montage = elem.children(".show_montage");
                        const start_montage = elem.children(".start_montage");

                        if (data[ss_id].islocked) {
                            elem.css("background", "#141628")
                                .css("pointer-events", "none")
                                .css("cursor", "default")
                                .data("ss_locked", "True");
                        } else if (data[ss_id].exists) {
                            elem.css("background", "#FFFFFF")
                                .css("pointer-events", "auto")
                                .data("ss_locked", "False");
                            start_montage.hide();
                            show_montage.show();
                        } else {
                            elem.css("background", "#FFFFFF")
                                .css("pointer-events", "auto")
                                .data("ss_locked", "False");
                            show_montage.hide();
                            start_montage.show();
                        }
                    });
                }
            });
        }, 1000);
    });

    $(document).keypress(function (event) {
        if (event.which === 32 && event.target.type !== "text" && event.target.type !== "textarea") {
            event.preventDefault();
        }
    });

    $(document).keyup(function (event) {
        if ($(".modal").length > 0) { //to disable handler when dialog is open
            return false;
        }

        if (event.target.type === "text" || event.target.type === "textarea")  {
            return false;
        }

        if (!$('br').is('.step_view')) { //to disable handler on other pages
            return false;
        }

        event.stopImmediatePropagation();
        if (event.which === 32) {
            if (!isRecording)
                $(".start_recording").trigger("click");
            else
                $(".stop_recording").trigger("click");
        }
    });

    $(".start_recording").off().on("click", function(){
        start_rec();
    });

    $(".stop_recording").off().on("click", function(){
        stop_rec();
    });

    $("#rename_step_form, #rename_lesson_form").off().on("keypress", function(e) {
        elem = $(this);
        var stepRenaming = (elem.attr("id") === "rename_step_form");
        if (e.keyCode === 13 && !e.shiftKey) {
            e.preventDefault();
            row = elem.parents(".ui-state-default");
            var name_new = elem.parents(".ui-state-default").find("#input_field_name").val();
            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "/rename-elem/",

                data: {
                    "id": stepRenaming ? elem.parents(".ui-state-default").attr("stepID") : elem.parents(".ui-state-default").attr("lessonID"),
                    "type": stepRenaming ? "step" : "lesson",
                    "name_new": name_new
                },
                success: function (data) {
                    $("#cancel-rename").trigger( "click", name_new );
                    elements_subscriptor();
                },
                error: function(request, status, errorThrown) {
                    alert(request.responseText);
                }
            });
        }
    });

    $("#rename-substep-template-form").off().on("keypress", function(e) {
        elem = $(this);
        var stepRenaming = (elem.attr("id") === "rename_step_form");
        if (e.keyCode === 13 && !e.shiftKey) {
            e.preventDefault();
            const name_new = elem.find("#input_field_name").val();

            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "update_substep_template/",

                data: {
                    "template": name_new
                },
                success: function () {
                    $("#cancel-rename").trigger( "click", name_new );
                    elements_subscriptor();
                },
                error: function(request) {
                    alert(request.responseText);
                }
            });
        }
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

   function noBack(){window.history.forward();}
   noBack();
   window.onload=noBack;
   window.onpageshow=function(evt){if(evt.persisted)noBack();}
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


