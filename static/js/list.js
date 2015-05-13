$(document).ready(function(){
    var $t = $(this);
    $("#sortable").sortable({
        stop : function(event, ui) {
            $.ajax({
                beforeSend: function(xhr) {
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
                },
                //alert("in ajax");
                type: "POST",
                url: "/reorder_lists/",

                data: {"order": $(this).sortable("toArray"), "ids": $(this).sortable("toArray", {attribute: 'lessonID'})},
                success: function(data){
                        alert(data);
                }
            });
        }

    });

    $("#sortable").disableSelection();

    $('.rename_button').on('click', function(e){
        e.stopPropagation();
        $(this).parent().parent().find("a").replaceWith('<form id="rename_lesson_form" action="/rename_lesson" method="post">' +
        '<input type="text"></form> ');
    });

    $(".lesson_info").on('click',function(){
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

    setInterval(function() {
        var seconds = new Date().getTime() / 1000;
        var elem = $('#timer');
        elem.text(rectime(parseInt(seconds - elem.data('starttime'))));
    }, 1000); // 60 * 1000 milsec

//    window.onbeforeunload = function() { return "You work will be lost."; };
   function noBack(){window.history.forward();}
   noBack();
   window.onload=noBack;
   window.onpageshow=function(evt){if(evt.persisted)noBack();}
   window.onunload=function(){void(0);}
});


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
