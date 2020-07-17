$(document).ready(setup)

function setup() {
    let top = $('#top'), bottom = $('#bottom'), bar = $('.bar');
    let session = $('#updater').data('session').toString();

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
                            bar.fadeIn()
                        }
                    } else if (data['state'] === "Blank") {
                        if (state === "Init" || state === "Active") {
                            bar.fadeOut({
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
                            bar.fadeIn()
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