var application = function(){
    
    /*
     * QiSession event
     */
    var services = {};
    var onConnected = function(session){
        console.log("Connected !");
        var acceptable_tries = 10;
        function checkConnectionGauge() {
            RobotUtils.onService(function (ALPepperBeats) {
                $("#noservice").hide();
                services.ALPepperBeats = ALPepperBeats;
                ALPepperBeats.get().then(function(level) {
                    // Find the button with the right level:
                    $(".levelbutton").each(function() {
                        var button = $(this);
                        if (button.data("level") == level) {
                            button.addClass("highlighted");
                            button.addClass("clicked");
                        }
                    });
                    // ... and show all buttons:
                    $("#buttons").show();
                });
                $(".levelbutton").click(function() {
                    // grey out the button, until we hear back that the click worked.
                    var button = $(this);
                    var level = button.data("level");
                    $(".levelbutton").removeClass("highlighted");
                    $(".levelbutton").removeClass("clicked");
                    button.addClass("clicked");
                    ALPepperBeats.set(level).then(function(){
                        button.addClass("highlighted");
                    });
                })
            }, function() {
                // We failed to get the service, wait again, and try again
                // We display an error message after a while.
                if (acceptable_tries > 0) {
                    acceptable_tries -= 1;
                    setTimeout(checkConnectionGauge, 200);
                } else {
                    $("#noservice").show();
                    setTimeout(checkConnectionGauge, 2000);
                }
            });
        }
        checkConnectionGauge();
        RobotUtils.onService(function (ALTabletService) {
            services.ALTabletService = ALTabletService;
        });
        
        $("#exit").click(function() {
            if (services.ALPepperBeats) {
                services.ALPepperBeats.stop();
            }
            if(services.ALTabletService) {
                services.ALTabletService.hideWebview();
            }
        });
    };
    
    var onError = function(){
        console.log("Disconnected, or failed to connect :-(");
    }

    RobotUtils.connect(onConnected, onError);
};
