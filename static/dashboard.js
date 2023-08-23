
window.addEventListener('load', init, false);

const api_key_promise =  get_api(api_key_endpoint);

let api_key;
let api_key_bearer;

async function get_api(endpoint) {
    const response = await fetch(endpoint, {
        method: 'GET',
        headers: {}
    });
    const response_json = await response.json();
    return response_json['api_key'];
}

async function load_containers() {
    const response = await fetch(api_list_containers_endpoint, {
        method: 'GET',
        headers: {
            Authentication: api_key_bearer
        }
    });
    const response_json = await response.json();
    if (response.status !== 200 || !response.ok) {
        if (response_json.contains('message')) {
            throw new Error(response_json['message']);
        }
        throw new Error("Unknown Error");
    }

    return response_json;
}

function message(msg) {
    // TODO: display message in an html element on the page (needed)??
    alert(msg)

}

function set_container_view(containers) {
    const container_area = document.getElementById('container_list');
    let html = "";
    for (const category in containers) {
        // console.log(containers[category]);
        html += `<button type="button" class="collapsible text-center fw-bold btn btn-secondary"> ${category} </button>`;
        html += `<div class="container_content"><ul class="list-group list-group-flush">`;
        for (const container of containers[category]) {
            // console.log(container['short_id']);
            html += '<li class="list-group-item text-center fw-bold"><div><ul class="list-group list-group-horizontal">'
            html += `<li class="list-group-item border-0" style="width: 10%"><p class="text-center fw-bold"> ${container['short_id']} </p></li>`;
            html += `<li class="list-group-item border-0" style="width: 15%"><p class="fw-bold"> ${container['name']} </p></li>`;
            html += `<li class="list-group-item border-0" style="width: 15%"><p class="fw-bold"> ${container['image']} </p></li>`;
            html += `<li class="list-group-item border-0" style="width: 10%"><p class="fw-bold"> Created ${container['created_at']} </p></li>`;
            html += `<li class="list-group-item border-0" style="width: 10%"><p class="fw-bold"> ${container['status_repr']} </p></li>`;
            if (container['status'] === 'running') {
                html += `<li class="list-group-item border-0" style="width: 15%">
                        <button type="button" style="width: 100%; height: 50%" class="btn btn-danger fw-bold stop_btn" id="${container['short_id']}"> Stop Container </button>
                        <button type="button" style="width: 100%; height: 50%" class="btn btn-warning fw-bold restart_btn" id="${container['short_id']}"> Restart Container </button>
                        </li>`;
            } else if (container['status'] === 'exited') {
                html += `<li class="list-group-item border-0" style="width: 15%"><button type="button" style="width: 100%" class="btn btn-success fw-bold start_btn" id="${container['short_id']}"> Start Container </button></li>`;
            }
            html += `<li class="list-group-item border-0" style="width: 25%"><p class="fw-bold"> ${container['ports']} </p></li>`;


            html += '</ul></div></li>'
        }
        html += "</ul></div>";
    }

    container_area.innerHTML = html;

    let category_collapsible = document.getElementsByClassName("collapsible");

    for (let container_html of category_collapsible) {
        container_html.addEventListener("click", function() {
            this.classList.toggle("active");
            let content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else if (content.style.display === "none") {
                content.style.display = "block";
            } else {
                content.style.display = "none";
            }
        });
    }

    let restart_btns = document.getElementsByClassName("restart_btn");
    let start_btns = document.getElementsByClassName("start_btn");
    let stop_btns = document.getElementsByClassName("stop_btn");

    for (let btn of restart_btns) {
        btn.addEventListener("click", function() {
            console.log(this.id);
            // TODO: do api call, same for all below. remember add api key, if succeed, update UI, if not, display warning message
        });
    }

    for (let btn of start_btns) {
        btn.addEventListener("click", function() {
            console.log(this.id);
        });
    }

    for (let btn of stop_btns) {
        btn.addEventListener("click", function() {
            console.log(this.id);
        });
    }



}

async function init() {
    api_key_promise.then((key) => {
        api_key = key;
        api_key_bearer = `Bearer ${api_key}`
        return load_containers();
    }).then((containers) => {
        set_container_view(containers);
    }).catch((err) => {
        message(err);
    })
}