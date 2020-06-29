function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            var csrftoken = getCookie('csrftoken');
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function () {
    console.log("Starting");
    setup();
});

function updateDisplay(data) {
    $("#count-val").text(data['count']);
}

function inc() {
    send(1)
}

function dec() {
    send(-1)
}

function send(delta) {
    $.ajax({
        url: '/api/count/update/',
        method: 'POST',
        dataType: 'json',
        data: {
            'change': delta,
        },
        success: updateDisplay,
    })
}

function check() {
    $.ajax({
        url: '/api/count/get/',
        dataType: 'json',
        type: 'get',
        success: updateDisplay,
    })
}

function setup() {
    let poll = function () {
        check();
    };
    let pollInterval = setInterval(function () { // run function every 500 ms
        poll();
    }, 500);
    poll(); // also run function on init
}