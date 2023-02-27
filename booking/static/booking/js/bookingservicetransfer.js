(function($) {
    var time_autofilled = false;

    $(document).ready(function() {
        $(service_form_selector + " #id_time").after(
            "<button class='btn btn-success btn-copy btn-copy-time'><<</button><span class='computed-value'>Calculated: <b data-computed=time>N/A</b></span>"
        );
        var computedTime = $("b[data-computed=time]");
        var timeInput = $("#id_time")[0];
        var timeFromInput = $("#id_schedule_time_from");
        var timeToInput = $("#id_schedule_time_to");

        function compare_time(evt) {
            // a function to check if computed values differ from set values
            // it highlights different values
            if (timeInput.value == "") {
                if (is_time(computedTime.html())) {
                    timeInput.value = computedTime.html();
                    time_autofilled = true;
                    $(".btn-copy-time").removeClass("btn-danger");
                    $(".btn-copy-time").removeClass("btn-warning");
                    $(".btn-copy-time").addClass("btn-success");
                    return 0;
                }
                time_autofilled = false;
                $(".btn-copy-time").removeClass("btn-danger");
                $(".btn-copy-time").removeClass("btn-warning");
                $(".btn-copy-time").removeClass("btn-success");
                return 0;
            }
            if (time_autofilled) {
                if (evt.target.id != "id_time") {
                    if (is_time(computedTime.html())) {
                        timeInput.value = computedTime.html();
                        $(".btn-copy-time").removeClass("btn-danger");
                        $(".btn-copy-time").removeClass("btn-warning");
                        $(".btn-copy-time").addClass("btn-success");
                        return 0;
                    }
                    timeInput.value = "";
                    $(".btn-copy-time").removeClass("btn-danger");
                    $(".btn-copy-time").removeClass("btn-warning");
                    $(".btn-copy-time").removeClass("btn-success");
                    return 0;
                }
                time_autofilled = false;
            }
            return compare_time_values();
        }

        function compare_time_values() {
            if (is_time(timeInput.value) && is_time(computedTime.html())) {
                iseconds = seconds(timeInput.value);
                cseconds = seconds(computedTime.html());
                if (iseconds == cseconds) {
                    $(".btn-copy-time").removeClass("btn-danger");
                    $(".btn-copy-time").removeClass("btn-warning");
                    $(".btn-copy-time").addClass("btn-success");
                    return 0;
                }
                if (iseconds < cseconds) {
                    if (cseconds - iseconds < 6 * 3600) {
                        $(".btn-copy-time").removeClass("btn-danger");
                        $(".btn-copy-time").removeClass("btn-success");
                        $(".btn-copy-time").addClass("btn-warning");
                        return 0;
                    }
                    $(".btn-copy-time").removeClass("btn-success");
                    $(".btn-copy-time").removeClass("btn-warning");
                    $(".btn-copy-time").addClass("btn-danger");
                    return 0;
                }
                if (iseconds - cseconds > 18 * 3600) {
                    $(".btn-copy-time").removeClass("btn-danger");
                    $(".btn-copy-time").removeClass("btn-success");
                    $(".btn-copy-time").addClass("btn-warning");
                    return 0;
                }
                $(".btn-copy-time").removeClass("btn-success");
                $(".btn-copy-time").removeClass("btn-warning");
                $(".btn-copy-time").addClass("btn-danger");
                return 0;
            }
            $(".btn-copy-time").removeClass("btn-danger");
            $(".btn-copy-time").removeClass("btn-warning");
            $(".btn-copy-time").removeClass("btn-success");
            return 0;
        }

        function is_time(str) {
            if (str == "") {
                return true;
            }
            var parts = str.split(":");
            for (let index = 0; index < parts.length; index++) {
                if (parts[index] && isNaN(parts[index])) {
                    return false;
                }
            }
            return true;
        }

        function seconds(str) {
            if (str == "") {
                return 0;
            }
            var parts = str.split(":");
            result = 0;
            for (let index = 0; index < parts.length; index++) {
                n = Number(parts[index]);
                m = 1;
                if (index == 0) {
                    m = 3600;
                } else if (index == 1) {
                    m = 60;
                }
                if (isNaN(n)) {
                    return 0;
                } else {
                    result += m * n;
                }
            }
            return result;
        }

        function get_computed_time(evt) {
            computedTime.html("Loading...");
            // sending a request to get computed value
            $.ajax({
                    url: bookingservicetransfer_time_url,
                    async: true,
                    datatype: "json",
                    type: "POST",
                    data: $(service_form_selector).serialize(),
                })
                .done(function(data) {
                    if (data["time"]) {
                        computedTime.html(data["time"]);
                    } else {
                        computedTime.html(data["time_message"]);
                    }
                    compare_time(evt);
                })
                .fail(function() {
                    computedTime.html("N/A");
                    compare_time(evt);
                });
        }

        function get_time_from(evt) {
            // sending a request to get time from value
            $.ajax({
                url: bookingservicetransfer_schedule_from_url,
                async: true,
                datatype: "json",
                type: "POST",
                data: $(service_form_selector).serialize(),
            }).done(function(data) {
                if (data["time"]) {
                    timeFromInput.val(data["time"]).trigger("change");
                }
            });
        }

        function get_time_to(evt) {
            // sending a request to get time from value
            $.ajax({
                url: bookingservicetransfer_schedule_to_url,
                async: true,
                datatype: "json",
                type: "POST",
                data: $(service_form_selector).serialize(),
            }).done(function(data) {
                if (data["time"]) {
                    timeToInput.val(data["time"]).trigger("change");
                }
            });
        }

        get_computed_time();

        // for times changed by calendar
        $("#id_schedule_time_from").focusout(function(evt) {
            evt.preventDefault();
            get_computed_time(evt);
        });
        $("#id_schedule_time_to").focusout(function(evt) {
            evt.preventDefault();
            get_computed_time(evt);
        });

        $(
            service_form_selector +
            " input, " +
            service_form_selector +
            " select"
        ).on("change", function(evt) {
            get_computed_time(evt);
        });

        $("#id_schedule_from").on("change", function(evt) {
            get_time_from(evt);
        });

        $("#id_schedule_to").on("change", function(evt) {
            get_time_to(evt);
        });

        $(".btn-copy-time").on("click", function(evt) {
            evt.preventDefault();
            if (is_time(computedTime.html())) {
                timeInput.value = computedTime.html();
            }
            compare_time(evt);
        });
    });
})(jQuery);