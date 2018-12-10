function getCookie(xhr) {
    var cookie = null;
    var cookVal = null;
    var cookies = document.cookie.split(";");

    for (var i = 0; i < cookies.length; i++) {
        cookie = jQuery.trim(cookies[i]);

        if (cookie.substring(0, "csrftoken".length + 1) === "csrftoken=") {
            cookVal = decodeURIComponent(cookie.substring("csrftoken".length + 1));
            break;
        }
    }
    xhr.setRequestHeader("X-CSRFToken", cookVal)
}

function rectime(sec) {
    var hr = Math.floor(sec / 3600);
    var min = Math.floor((sec - (hr * 3600)) / 60);
    sec -= ((hr * 3600) + (min * 60));
    sec += "";
    min += "";
    while (min.length < 2) {
        min = "0" + min;
    }
    while (sec.length < 2) {
        sec = "0" + sec;
    }
    hr = (hr) ? hr + ":" : "";
    return hr + min + ":" + sec;
}
