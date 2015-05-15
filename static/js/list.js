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

var elements_subscriptor = function() {
        sortObj = $("#sortable");

    $("#sortable").sortable({
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

    $("#sortable").disableSelection();

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

    $('#cancel-rename').off().live('click', function(){
        $(this).fadeOut("fast",  function(){
            $(this).parent().parent().parent().html(deleted_element);
            elements_subscriptor();
        });
    });


    $(".lesson_info").off().on('click',function(){
        $(this).parent().find('.lesson_path').toggleClass('hiddenInfo');
        $(this).parent().find('.lesson_info_link').toggleClass('hiddenInfo');
        $(this).parent().find("a").toggleClass('hiddenInfo');
    }).css('cursor','pointer');

    $('.delete_button').on('click', function(){
        var redir_url = $(this).find(".delete-url").data("urllink");
        $(this).append("<div class='modal'> Confirm Dialog Box</div>");
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
                        console.log(redir_url)
                },
                    "No": function () {
                    $(this).dialog('close');
                }
            }
        });
    });

    function fader(el) {
        el.fadeTo("fast", .5).removeAttr("href");
    }

    $('.start-recording').on('click', function(){
        $(this).text("Starting...").click(function(){
                return false;
        });
        var el = $(this);
        setTimeout(fader, 0, el);
    });

    $('.stop-recording').on('click', function(){
        $(this).text('Preparing...');
        var el = $(this);
        setTimeout(fader, 0, el);
    });

    $('#rename-step-form').off().on('keypress', function(e) {
        elem = $(this);
        if (e.keyCode == 13 && !e.shiftKey) {
            e.preventDefault();
            $.ajax({
                beforeSend: cookie_csrf_updater,
                type: "POST",
                url: "/rename_elem/",

                data: {
                    "id": elem.parents('.ui-state-default').attr('id'),
                    "type": 'step',
                    "name_new": elem.parents('.ui-state-default').find('#input-field-name').val()
                },
                success: function (data) {
                    elements_subscriptor();
                    elem.parents('.ui-state-default').attr('id');
                    $('#cancel-rename').trigger( "click" );
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


