
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

function make_row(container) {
    let html = `<ul id="${container['short_id']}" class="list-group list-group-horizontal row">`;
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
    html += `<li class="list-group-item border-0" style="width: 25%"><p class="fw-bold"> ${container['ports']} </p></li></ul>`;
    return html
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
            html += `<li class="list-group-item text-center fw-bold"><div>`;
            html += make_row(container);

            html += '</div></li>'
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



    for (let mode of ["restart_btn", "start_btn", "stop_btn"]) {
        let btns = document.getElementsByClassName(mode);

        for (let btn of btns) {
            btn.addEventListener("click", async function() {
                console.log(api_cache[mode]);
                const response = await fetch(api_cache[mode], {
                    method: 'POST',
                    headers: {
                        Authentication: api_key_bearer,
                        "content-type": "application/json"
                    },
                    body: JSON.stringify({
                        container_id: this.id
                    })
                });
                const response_json = await response.json();
                if (response.status !== 200 || !response.ok) {
                    if (response_json.contains('message')) {
                        message(response_json['message']);
                    }
                    message("Unknown Error");
                }

                let row = document.getElementById(this.id);

                row.innerHTML = make_row(response_json);
                let btn_col = row.children[0].children[5];
                if (response_json['status'] === 'running') {
                    let stop_btn = btn_col.children[0];
                    stop_btn.addEventListener("click", btn_listener_closure("stop_btn", this.id));
                    let restart_btn = btn_col.children[1];
                    stop_btn.addEventListener("click", btn_listener_closure("restart_btn", this.id));
                } else if (response_json['status'] === 'exited') {
                    let start_btn = btn_col.children[0];
                    start_btn.addEventListener("click", btn_listener_closure("start_btn", this.id));
                }
            });
        }
    }

}

function btn_listener_closure(api_mode, container_id) {
    return async function() {
        console.log(api_cache[api_mode]);
        const response = await fetch(api_cache[api_mode], {
            method: 'POST',
            headers: {
                Authentication: api_key_bearer,
                "content-type": "application/json"
            },
            body: JSON.stringify({
                container_id: container_id
            })
        });
        const response_json = await response.json();
        if (response.status !== 200 || !response.ok) {
            if (response_json.contains('message')) {
                message(response_json['message']);
            }
            message("Unknown Error");
        }
        let row = document.getElementById(this.id);
        row.innerHTML = make_row(response_json);
        console.log(row);
        console.log(row.children);
        console.log(row.children[0].children[5]);
        let btn_col = row.children[0].children[5];
        if (response_json['status'] === 'running') {
            let stop_btn = btn_col.children[0];
            stop_btn.addEventListener("click", btn_listener_closure("stop_btn", container_id));
            let restart_btn = btn_col.children[1];
            stop_btn.addEventListener("click", btn_listener_closure("restart_btn", container_id));
        } else if (response_json['status'] === 'exited') {
            let start_btn = btn_col.children[0];
            start_btn.addEventListener("click", btn_listener_closure("start_btn", container_id));
        }
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

