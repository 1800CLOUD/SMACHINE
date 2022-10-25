var doc = document;
var country = doc.getElementById('h_country');
var state = doc.getElementById('h_state');
var reentry = doc.getElementById('h_reentry');

$(document).ready(
    function () {
        $("#h_product").select2();
        $("#h_city").select2();
        $("#h_technician").select2();

        $("#s2id_h_product").removeClass("s_website_form_input");
        $("#s2id_h_city").removeClass("s_website_form_input");
        $("#s2id_h_technician").removeClass("s_website_form_input");
    }
);

doc.getElementById("h_button_submit").addEventListener('click', function () {
        console.log("Click Summit");
        $("#s2id_h_product").removeClass("s_website_form_input");
        $("#s2id_h_city").removeClass("s_website_form_input");
        $("#s2id_h_technician").removeClass("s_website_form_input");
    }
);

country.addEventListener('change', function () {
        var country_id = country.value;
        var url = "/helpdesk_form/filter_field/";
        var param = {
            "value": parseInt(country_id),
            "field": "country_id",
            "model": "res.country.state"
        };
        filter_field(state, url, param);
    }
);

state.addEventListener('change', function () {
        var city = doc.getElementById('h_origin_city');
        var state_id = state.value;
        var domain = "[('state_id','=', " + state_id + ")]"
        var url = "/helpdesk_form/filter_field/";
        var param = {
            "value": parseInt(state_id),
            "field": "state_id",
            "domain": domain,
            "model": "res.city"
        };
        filter_field(city, url, param);
    }
);

reentry.addEventListener('change', function () {
        if (reentry.checked === true) {
            $("#div_ticket").removeClass("d-none");
            $("#h_ticket").prop("required", true);

            var vat = $("#h_doc_id").val() || 0;
            var doc_type = $("#h_doc_type").val() || 0;
            var url = "/helpdesk_form/partner_tickets/";
            var param = {
                "vat": vat,
                "doc_type": doc_type,
            };
            filter_field(doc.getElementById("h_ticket"), url, param);
        }
        else {
            $("#div_ticket").addClass("d-none");
            $("#h_ticket").prop("required", false);
        }
    }
);

function filter_field(element, url, param) {
    var params = JSON.stringify({
            "jsonrpc": "2.0",
            "params": param,
        }
    );
    var request = new Request(
        url, 
        {
            method: 'POST',
            body: params,
            headers: new Headers({
                "Content-Type": "application/json"
            }),
        async: false
    });
    fetch(request)
        .then(function (response) 
        {
            // console.log(
            //     "Filtro por departamento - OK:", response.ok, 
            //     "- status:", response.status, 
            //     "- statusText:", response.statusText,
            //     "- response: ", response);
            return response.json();
        })
        .then(function (returnedValue) 
        {
            console.log(returnedValue);
            clear_childs(element);
            var result = returnedValue.result || [];
            fill_data_field(element, result);
        })
        .catch( function (error)
        {
            console.error("ERROR "+ url + "!!!: ", error);
        }
    );
};

function fill_data_field(element, data) {
    var option_empty = doc.createElement('option');
    option_empty.value = "";
    option_empty.innerHTML = "-";
    element.appendChild(option_empty);
    for (var line of data) {
        var option = doc.createElement('option');
        option.value = line[0];
        option.innerHTML = line[1];
        element.appendChild(option);
    }
};

function clear_childs (element)
{
    while (element.firstChild) 
    {
        element.removeChild(element.firstChild);
    }
};
console.log(country)

