let scene_index = 0;
let locked = false;

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
    console.log(order);
    check();
});

function updateDisplay(data) {
    let top = $('#top'), bottom = $('#bottom');
    if (data['state'] === "Init") {
        top.text("Initialising");
        bottom.text(session);
    } else if (data['state'] === "Active") {
        top.text(data['l1']);
        bottom.text(data['l2']);
    } else {
        top.text("");
        bottom.text("");
    }

    // update scene list active to scene selection
    $(".scenechange").removeClass('active');
    let program = sceneToProgram(data['scene']);
    $("#scene-" + program.toString()).addClass('active');

    // update internal variables to reflect state
    current_state = data['state'];
    scene_index = program;

    let adjacent = adjacentPrograms();
    if (adjacent.prev === null)
        $('#previous').prop('disabled', true);
    else
        $('#previous').prop('disabled', false);

    if (adjacent.next === null)
        $('#next').prop('disabled', true);
    else
        $('#next').prop('disabled', false);

    if (current_state === "Blank")
        $('#blank').html('<i class="fas fa-play" title="Un-Blank"></i>');
    else
        $('#blank').html('<i class="fas fa-pause" title="Blank"></i>');

}

function showblank() {
    if (locked) return;

    if (current_state === "Blank")
        send(order.get(scene_index), "Active");
    else
        send(order.get(scene_index), "Blank");
}

function scenechange(program) {
    if (locked) return;

    scene_index = program;
    direct(order.get(program));
}

function showprevious() {
    if (locked) return;

    let l = adjacentPrograms().prev
    if (l !== null) {
        scene_index = l;
        direct(order.get(l))
    }
}

function shownext() {
    if (locked) return;

    let l = adjacentPrograms().next;
    if (l !== null) {
        scene_index = l;
        direct(order.get(l))
    }
}

function direct(scene) {
    if (current_state === "Active") {
        send(scene, "Blank");
        lock();
        setTimeout(() => {
            unlock();
            send(scene, "Active");
        }, 1000);
    } else {
        send(scene, "Active");
    }
}

function lock() {
    $('.control').addClass('disabled');
    locked = true;
}

function unlock() {
    $('.control').removeClass('disabled');
    locked = false;
}

function sceneToProgram(scene) {
    let first = null;
    let next = null;
    for (let index of order) {
        if (index[1] === scene) {
            if (index[0] >= scene_index && next === null) {
                next = index[0]
            }
            if (first === null) {
                first = index[0]
            }
        }
    }
    if (next === null)
        return first;
    else
        return next;
}

function adjacentPrograms() {
    let keys = Array.from(order.keys());
    let index = keys.indexOf(scene_index);
    let prev = null, next = null;
    if (index > 0)
        prev = keys[index - 1];
    if (index < keys.length-1)
        next = keys[index + 1];

    return {next: next, prev: prev}
}

function send(scene, state) {
    $.ajax({
        url: '/api/update/',
        method: 'POST',
        dataType: 'json',
        data: {
            'session': session,
            'key': api_key,
            'scene': scene,
            'state': state,
        },
        success: updateDisplay,
    })
}

function check() {
    $.ajax({
        url: '/api/session_state/',
        dataType: 'json',
        type: 'get',
        data: {'session': session},
        success: updateDisplay,
    })
}
