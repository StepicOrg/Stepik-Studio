var global_html;

$(function  () {

    var context_tmplt = [{name:'NoName'}];
    var compiledTemplate = JST['static/extra/hb_templates/test.handlebars'];
    global_html = compiledTemplate(context_tmplt);
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
            $(replace).find('.lesson_name').html(new_name);
            deleted_element = replace.html();
        }
        return deleted_element;
    }

function record_started(callback)
{
    $('.start-recording').removeClass('start-recording').addClass('stop-recording').text('Recording');
    var curr_sec_from_epoch = new Date().getTime() / 1000;
    $('.stop-recording').append('<div id = "timer" data-starttime='+curr_sec_from_epoch+'>00:00</div>');
    callback();
}

function record_stopped(callback)
{
    $('.stop-recording').removeClass('stop-recording').addClass('start-recording').text('Start Recording');
    callback();
}

var elements_subscriptor = function() {
    sortObj = $("#sortable");

    sortObj.sortable({
        stop : function(event, ui) {
            $.ajax({
                beforeSend: cookie_csrf_updater,
                //alert("in ajax");
                type: "POST",
                url: "/reorder_lists/",

                data: {"order": $(this).sortable("toArray"), "ids": $(this).sortable("toArray", {attribute: 'lessonID'})},
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
        deleted_element = $(this).parent().parent().html();
        var name = $(this).parents('.ui-state-default').find(".lesson_name").text();
        $(this).fadeOut("fast",  function(){
            $(this).parent().parent().html(global_html);
            elements_subscriptor();
            $('#input-field-name').val(name);
            });
        });

    $('#cancel-rename').off().live('click', function(event, new_name){
        $(this).fadeOut("fast",  function(){
            deleted_element = upd_deleted_el(new_name, deleted_element);
            $(this).parents('.input-step-name-field').html(deleted_element);
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
        $(this).append("<div class='modal'> Action can't be undone. Are you sure?</div>");
        $(this).find(".modal").dialog({
            resizable: false,
            modal: true,
            title: "Delete?",
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

    function fader(el,callback) {
        el.fadeTo("fast", .5).removeAttr("href");
        callback();
    }

    $('.start-recording').off().on('click', function(){
        $(this).text("Starting...").click(function(){
                return false;
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
                alert("Server Error!");
            }
        });
                        //            var el = $(this);
                //setTimeout(fader, 0, el);
    });

    $('.stop-recording').off().on('click', function(){
        $(this).text('Preparing...').click(function(){
                return false;
        });
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
                alert("Server Error!");
            }

        });
    });

    $('#rename-step-form').off().on('keypress', function(e) {
        elem = $(this);
        if (e.keyCode == 13 && !e.shiftKey) {
            e.preventDefault();
            row = elem.parents('.ui-state-default');
            var name_new = elem.parents('.ui-state-default').find('#input-field-name').val();
            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "/rename_elem/",

                data: {
                    "id": elem.parents('.ui-state-default').attr('id'),
                    "type": 'step',
                    "name_new": name_new
                },
                success: function (data) {
                    $('#cancel-rename').trigger( "click", name_new );
                    elements_subscriptor();
                },
                error: function(request,status,errorThrown) {
                    alert("Cant rename :" + status + " " + errorThrown);
                }
            });
        }
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


