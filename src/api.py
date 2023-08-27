import os
from flask import Blueprint, jsonify, request
from .authentication import allowed_addr_only, User, api_key_required
from flask_login import login_required
from .docker_wrapper import Docker

api = Blueprint(os.getenv('API_BLUEPRINT_NAME', 'api'), __name__)

endpoints = {
    'api_key': '/api/v0/get_api_key',
    'all_containers': '/api/v0/get_info_of_all_containers',
    'stop_container': '/api/v0/stop_container',
    'start_container': '/api/v0/start_container',
    'restart_container': '/api/v0/restart_container',
}


@api.route(endpoints['api_key'], methods=['GET'])
@allowed_addr_only
@login_required
def get_web_api_key():
    """
    invalidate previous api key everytime user get to the dashboard

    this is saying, if user refresh the dashboard page, or it opens another dashboard page, they will lose
    the old key, only ONE ACTIVE dashboard page is allowed

    """
    user = User()
    user.api_key.update_key()
    return jsonify({'api_key': user.api_key.key}), 201


@api.route(endpoints['all_containers'], methods=['GET'])
@allowed_addr_only
@api_key_required
def list_containers():

    docker_client = Docker()
    # containers = docker_client.

    return jsonify(docker_client.load_all_containers()), 200


@api.route(endpoints['stop_container'], methods=['POST'])
@allowed_addr_only
@api_key_required
def stop_container():
    container_id = request.get_json().get("container_id", None)
    docker_client = Docker()
    docker_success = docker_client.stop_container(container_id)
    if docker_success:
        return jsonify(docker_client.get_container_json(container_id)), 200
    else:
        return {"message": f"failed to restart container {container_id}, possible that you haven't call list container before"}, 400


@api.route(endpoints['start_container'], methods=['POST'])
@allowed_addr_only
@api_key_required
def start_container():
    container_id = request.get_json().get("container_id", None)
    docker_client = Docker()
    docker_success = docker_client.start_container(container_id)
    if docker_success:
        return jsonify(docker_client.get_container_json(container_id)), 200
    else:
        return {"message": f"failed to restart container {container_id}, possible that you haven't call list container before"}, 400


@api.route(endpoints['restart_container'], methods=['POST'])
@allowed_addr_only
@api_key_required
def restart_container():
    container_id = request.get_json().get("container_id", None)
    docker_client = Docker()
    docker_success = docker_client.restart_container(container_id)
    if docker_success:
        return jsonify(docker_client.get_container_json(container_id)), 200
    else:
        return {"message": f"failed to restart container {container_id}, possible that you haven't call list container before"}, 400


