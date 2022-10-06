var doc = document;
var country = doc.getElementById('h_country');
var state = doc.getElementById('h_state');

$(document).ready(
    function () {
        $("#h_product").select2();
        $("#h_city").select2();
        $("#h_technician").select2();
    }
);

country.addEventListener('change', function () {
        var country_id = country.value;
        var param = {
            "value": parseInt(country_id),
            "field": "country_id",
            "model": "res.country.state"
        };
        filter_field(state, param);
    }
);

state.addEventListener('change', function () {
    var city = doc.getElementById('h_origin_city');
    var state_id = state.value;
    var param = {
        "value": parseInt(state_id),
        "field": "state_id",
        "model": "res.city"
    };
    filter_field(city, param);
}
);

function filter_field(element, param) {
    var params = JSON.stringify({
            "jsonrpc": "2.0",
            "params": param,
        }
    );
    var request = new Request(
        '/helpdesk_form/filter_field/', 
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
            console.error("ERROR STATE FILTER!!!: ", error);
        }
    );
};

function fill_data_field(element, data) {
    var option_empty = doc.createElement('option');
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

