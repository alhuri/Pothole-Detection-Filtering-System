$(document).ready(function () {


    $('input[name="daterange"]').daterangepicker({
        "showDropdowns": true,
        "showWeekNumbers": true,
        "alwaysShowCalendars": true,
        "startDate": "02/10/2021",
        "endDate": "02/24/2021"
    });


    var diag;
    document.getElementById("classifyBtn").onclick = function (e) {
        var drp = $('#dateCtrl').data('daterangepicker');
        var startDate = drp.startDate.toString();
        var endDate = drp.endDate.toString();
        if (!(moment(drp.startDate.toISOString()).isValid() && moment(drp.endDate.toISOString()).isValid())) {
            Swal.fire({
                icon: 'error',
                title: 'Selection Error',
                text: 'Invalid Date Selection.'
            });
        } else {
            Swal.fire({
                title: 'Fetching results please wait..',
                showConfirmButton: false,
                timerProgressBar: true,
                willOpen: () => {
                    Swal.showLoading();
                }
            });
            $.ajax({

                url: window.location.origin + "/classify", // the endpoint
                type: "POST", // http method
                data:
                    {"startDate": drp.startDate.toDate().toLocaleDateString(),
                    "endDate": drp.endDate.toDate().toLocaleDateString()
                    },
                success: function (json) {
                    var serials = 1;
                    var tbody = document.getElementById("tbody");
                    tbody.innerHTML = '';
                    json.predictions.forEach(function (e) {
                        var tr = document.createElement("tr");
                        var noTd = document.createElement("td");
                        var idTd = document.createElement("td");
                        var clsTd = document.createElement("td");
                        var dateTd = document.createElement("td");
                        noTd.innerHTML = serials;
                        serials +=1;
                        idTd.innerHTML = e.id;
                        clsTd.innerHTML = e.class;
                        dateTd.innerHTML = e.date;
                        tr.append(noTd);
                        tr.append(idTd);
                        tr.append(clsTd);
                        tr.append(dateTd);
                        tbody.appendChild(tr);
                    });
                    swal.close();

                },
                // handle a non-successful response
                error: function (xhr, errmsg, err) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error fetching data',
                        text: 'Error Code ' + xhr.status,

                    });
                }
            });


        }
    }
});