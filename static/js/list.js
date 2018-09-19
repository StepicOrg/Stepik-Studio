var rename_step_f_tmplt;
var rename_lesson_f_tmplt;
var rename_substep_tmplt_f_tmplt;

function isInstanceName(value){
  return !(value == null || value == ' ' || value =='  ' || value == '' || value == undefined);
}

$(function  () {
    var context_tmplt_1 = [{name:'NoName'}];
    var compiledTemplate_1 = JST['static/extra/hb_templates/renameStep.handlebars'];
    rename_step_f_tmplt = compiledTemplate_1(context_tmplt_1);

    var context_tmplt_2 = [{name:'NoName'}];
    var compiledTemplate_2 = JST['static/extra/hb_templates/renameLesson.handlebars'];
    rename_lesson_f_tmplt = compiledTemplate_2(context_tmplt_2);

    var context_tmplt_3 = [{name:'NoName'}];
    var compiledTemplate_3 = JST['static/extra/hb_templates/renameSubstepTemplate.handlebars'];
    rename_substep_tmplt_f_tmplt = compiledTemplate_3(context_tmplt_3);
});

var cookie_csrf_updater = function(xhr){
    var cookie = null;
    var cookVal = null;
    var cookies = document.cookie.split(';');

    for (var i=0; i < cookies.length; i++) {
        cookie = jQuery.trim(cookies[i]);

        if(cookie.substring(0, "csrftoken".length+1) == "csrftoken=") {
            cookVal = decodeURIComponent(cookie.substring("csrftoken".length + 1));
            break;
        }

    }

    xhr.setRequestHeader("X-CSRFToken", cookVal)
};


    function upd_deleted_el(new_name, deleted_element) {
        if (new_name != null && new_name.length > 0) {
            var jq_deleted = $(deleted_element);
            var replace = $('<div/>').append(jq_deleted.clone());
            $(replace).find('.obj_name').html(new_name);
            deleted_element = replace.html();
        }
        return deleted_element;
    }

function record_started(callback)
{
    $('.start-recording').removeClass('start-recording').addClass('stop-recording').text('Recording. Press here to stop.');
    var curr_sec_from_epoch = new Date().getTime() / 1000;
    $('.stop-recording').append('<div id = "timer" data-starttime='+curr_sec_from_epoch+'>00:00</div>');
    callback();
}

function record_start_failed(callback)
{
    $('.start-recording').text('Start Recording');
    callback();
}

function record_stopped(callback)
{
    $('.stop-recording').removeClass('stop-recording').addClass('start-recording').text('Start Recording');
    callback();
}
/*
var handle_not_stopped = function()
{
    $.ajax({
        beforeSend: cookie_csrf_updater,
        type: "POST",
        url: "/stop_recording/",

        data: {
            "action": "stop"
        },
        success: function(data){
            alert("success")
            elements_subscriptor()
        },
        error: function(data){
            alert("error")
            elements_subscriptor()
        }
    });
}
*/

var elements_subscriptor = function() {
    sortObj = $("#sortable");

    sortObj.sortable({
        start: function(e, ui) {
            if (!$("#isDraggable").is(":checked")) {
                window.location = $(ui.item[0]).find("a").attr('href');
            }
        },
        stop : function(event, ui) {
            var reorderingSteps = $(ui.item[0]).find("a").hasClass('step_name');
            var reorderingType = reorderingSteps ? "step" : "lesson";
            $.ajax({
                beforeSend: cookie_csrf_updater,
                //alert("in ajax");
                type: "POST",
                url: "/reorder_lists/",

                data: {"type": reorderingType, "order": $(this).sortable("toArray"), "ids": $(this).sortable("toArray",
                    {attribute: reorderingSteps ? 'stepID' : 'lessonID'})},
                success: function(data){
                        //alert(data);
                }
            });
        }

    });

    sortObj.disableSelection();

    var deleted_element;

    $('.rename_button').off().on('click', function(e){
        e.stopPropagation();
        var name = $(this).parents('.ui-state-default').find(".obj_name").text();
        $(this).fadeOut("fast",  function(){
            if ($(this).hasClass('step_rename')) {
                deleted_element = $(this).parent().parent().html();
                $(this).parent().parent().html(rename_step_f_tmplt);
            }
            else if ($(this).hasClass('lesson_rename')) {
                deleted_element = $(this).parent().parent().html();
                $(this).parent().parent().html(rename_lesson_f_tmplt);
            } else if ($(this).hasClass('substep_tmpl_rename')) {
                deleted_element = $(this).parent().html();
                $(this).parent().html(rename_substep_tmplt_f_tmplt);
            }
            else {
                alert("TEMPLATE ERROR!");
            }
            elements_subscriptor();
            $('#input-field-name').val(name);
            });
        });

    $('#cancel-rename').off().live('click', function(event, new_name){
        $(this).fadeOut("fast",  function(){
            deleted_element = upd_deleted_el(new_name, deleted_element);
            console.log('deleted_element:' , deleted_element);
            console.log('new_element:', new_name);
            $(this).parents('.input-step-name-field').html(deleted_element);
            $(this).parents('.input-lesson-name-field').html(deleted_element);
            $(this).parents('.rename-substep-template-field').html(deleted_element);
            elements_subscriptor();
        });
    });


    $(".lesson_info").off().on('click',function(){
        $(this).parent().find('.lesson_path').toggleClass('hiddenInfo');
        $(this).parent().find('.lesson_info_link').toggleClass('hiddenInfo');
        $(this).parent().find("a").toggleClass('hiddenInfo');
    });

    $('.delete_button').on('click', function(event){
        event.stopPropagation();
        var redir_url = $(this).find(".delete-url").data("urllink");
        var _ss_name = $(this).parents('.substep-list').find('.substep-name').text().split(/ /)[0];
        var _s_name = $(this).parents('.ui-state-default').find('.step_name').text();
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
            buttons: {
                    "Yes": function () {
                    $(this).dialog('close');
                    window.location.replace(redir_url);
                },
                    "No": function () {
                    $(this).dialog('close');
                }
            }
        });
    });

    function fader(el, callback) {
        el.fadeTo("fast", .5).removeAttr("href");
        callback();
    }

    $('.start-recording').off().on('click', function(){
        $(this).text("Starting...").click(function(){
                return false;
        });
        $(this).off();
        $(window).off().on('beforeunload', function(){
            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "/stop_recording/",

                data: {
                    "action": "stop"
                },
                success: function(data){
                    alert("success")
                    elements_subscriptor()
                },
                error: function(data){
                    alert("error")
                    elements_subscriptor()
                }
            });
        });
        $.ajax({
            beforeSend: cookie_csrf_updater,
            type: "POST",
            url: window.location.pathname,

            data: {
                "action": "start"
            },
            success: function(data){
                var el = $(this);
                setTimeout(fader, 0, el);
                record_started(elements_subscriptor);

            },
            error: function(data){
                alert(data.responseText);
                record_start_failed(elements_subscriptor);
            }
        });
    });

    $('.stop-recording').off().on('click', function(){
        $(this).text('Preparing...').click(function(){
                return false;
        });
        $(this).off();
        $(window).off('beforeunload');
        var el = $(this);
        $.ajax({
            beforeSend:function(jqXHR, settings) {
                cookie_csrf_updater(jqXHR);
                setTimeout(fader, 0, el);
            },
            type: "POST",
            url: window.location.pathname,


            data: {
                "action": "stop"
            },
            success: function(data){
                record_stopped(elements_subscriptor);
                location.reload(true);

            },
            error: function(data){
                alert(data.responseText);
            }

        });
    });

    $('#rename-step-form, #rename-lesson-form').off().on('keypress', function(e) {
        elem = $(this);
        var stepRenaming = (elem.attr("id") == "rename-step-form");
        if (e.keyCode == 13 && !e.shiftKey) {
            e.preventDefault();
            row = elem.parents('.ui-state-default');
            var name_new = elem.parents('.ui-state-default').find('#input-field-name').val();
            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "/rename_elem/",

                data: {
                    "id": stepRenaming ? elem.parents('.ui-state-default').attr('stepID') : elem.parents('.ui-state-default').attr('lessonID'),
                    "type": stepRenaming ? 'step' : 'lesson',
                    "name_new": name_new
                },
                success: function (data) {
                    $('#cancel-rename').trigger( "click", name_new );
                    elements_subscriptor();
                },
                error: function(request, status, errorThrown) {
                    alert(request.responseText);
                }
            });
        }
    });

    $('#rename-substep-template-form').off().on('keypress', function(e) {
        elem = $(this);
        var stepRenaming = (elem.attr("id") === "rename-step-form");
        if (e.keyCode === 13 && !e.shiftKey) {
            e.preventDefault();
            var name_new = elem.find('#input-field-name').val();
            console.log(name_new);
            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "update_substep_template/",

                data: {
                    "template": name_new
                },
                success: function (data) {
                    $('#cancel-rename').trigger( "click", name_new );
                    elements_subscriptor();
                },
                error: function(request, status, errorThrown) {
                    alert(request.responseText);
                }
            });
        }
    });

    $('#edit-text').click(function() {
        $('.form-edit-text').toggleClass('hiddenForm');
    });
};


var func_listener = function(){

    elements_subscriptor();


    setInterval(function() {
        var seconds = new Date().getTime() / 1000;
        var elem = $('#timer');
        elem.text(rectime(parseInt(seconds - elem.data('starttime'))));
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
	sec += ''; min += '';
	while (min.length < 2) {min = '0' + min;}
	while (sec.length < 2) {sec = '0' + sec;}
	hr = (hr)?':'+hr:'';
	return hr + min + ':' + sec;
}


