$(document).ready(setup)

function setup() {
    let top = $('#top'), bottom = $('#bottom'), bar = $('.bar');
    let session = $('#updater').data('session').toString();

    let searchParams = new URLSearchParams(window.location.search);
    let green = searchParams.has('green');

    if (green) {
        $('.main').addClass("green")
    }

    let fade_length = green ? 0 : 400;

    let state = "PreInit";
    if (session !== "") {
        let poll = function () {
            $.ajax({
                url: '/api/third/session_state/',
                dataType: 'json',
                type: 'get',
                data: {'session': session},
                success: function (data) {
                    if (data['state'] === "Init") {
                        top.text("Initialising");
                        bottom.text(session);
                        if (state === "PreInit" || state === "Blank") {
                            bar.fadeIn({duration: fade_length})
                        }
                    } else if (data['state'] === "Blank") {
                        if (state === "Init" || state === "Active") {
                            bar.fadeOut({
                                duration: fade_length,
                                done: function () {
                                    top.text("");
                                    bottom.text("");
                                }
                            });
                        }
                    } else if (data['state'] === "Active") {
                        top.text(data['l1']);
                        bottom.text(data['l2']);
                        if (state === "PreInit" || state === "Blank") {
                            bar.fadeIn({duration: fade_length})
                        }
                    }
                    state = data['state'];
                },
                error: function () { // error logging
                    console.log('Error!');
                    top.text("Error State");
                    bottom.text("");
                }
            });
        };
        let pollInterval = setInterval(function () { // run function every 500 ms
            poll();
        }, 500);
        poll(); // also run function on init
    } else {
        console.log('Blank Session!');
    }
}