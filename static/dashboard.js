
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
    // TODO: display message in an html element on the page

}

function set_container_view(containers) {
    console.log(containers);
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