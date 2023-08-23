import docker
from docker import DockerClient
import os
from datetime import datetime
import math

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

categories = {
    # keyword : title Todo: put this to a json file later
    'paperless_ngx': 'Paperless Ngx',
    'homeassistant': 'Home Assistant System',
    'hassio': 'Home Assistant System',
    'addon': 'Home Assistant Addon',
    'home': 'Homer Dashboard',
    'OpenBooks': 'OpenBooks',
    'nginxproxymanager': 'Nginx Proxy Manager',
    'photoprism': 'Photoprism',
    'vandam': 'Vandam',
    'gitea': 'Gitea',
    'nxtcloud': 'NextCloud',
}


class Docker:
    _instance = None

    def __new__(cls, host=os.getenv("DOCKER_HOST")):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(host)
        return cls._instance

    def _initialize(self, host):
        self._host = host
        self._loaded_containers = {}
        self._organized_container_info = {}
        try:
            if host == 'localhost':
                self._client = docker.from_env()
            else:
                self._client = DockerClient(host)
        except ConnectionError:
            print("GG")

    def load_all_containers(self):

        containers = self._client.containers.list(all=True)
        self._loaded_containers.clear()
        self._organized_container_info.clear()
        for _container in containers:
            container_json = Docker.jsonify_container(_container)
            self._loaded_containers[_container.short_id] = _container
            if title := Docker.get_category_title(container_json.get('name'), categories):
                if title not in self._organized_container_info:
                    self._organized_container_info[title] = []
                self._organized_container_info[title].append(container_json)

        return self._organized_container_info

    @staticmethod
    def get_category_title(name, category_dict):
        for keyword in category_dict:
            if keyword in name:
                return category_dict[keyword]

            # the below might be more efficient if zero-cost exception is implemented in python3.11
            # try:
            #     index = name.index(keyword)
            #     return category_dict[keyword]
            # except ValueError:
            #     pass

        return 'Misc'

    def list_loaded_containers_short_id(self):
        # return self.loaded_containers.keys()
        pass

    @staticmethod
    def jsonify_container(_container):

        container_json = {
            'id': _container.id,
            'short_id': _container.short_id,
            'name': _container.name,
            'image': Docker.extract_image(_container.image),  # currently only image name
            'status': _container.status,
            'created_at': f"{Docker.convert_time(_container.attrs['Created'])} Ago",
            'status_repr': (f"Up {Docker.convert_time(_container.attrs['State']['StartedAt'])}"
                            f"{'' if 'Health' not in _container.attrs['State'] else ' (' + _container.attrs['State']['Health']['Status'] + ') '}"),
        }

        if _container.status == 'running':
            container_json['status_repr'] = (f"Up {Docker.convert_time(_container.attrs['State']['StartedAt'])}"
                                             f"{'' if 'Health' not in _container.attrs['State'] else ' (' + _container.attrs['State']['Health']['Status'] + ') '}")
        elif _container.status == 'exited':
            container_json['status_repr'] = (f"Exited ({_container.attrs['State']['ExitCode']}) "
                                             f"{Docker.convert_time(_container.attrs['State']['StartedAt'])} Ago")

        extra_host = _container.attrs.get('HostConfig', None).get('ExtraHosts', None)
        if extra_host is not None:
            container_json['dependency'] = ", ".join(extra_host)

        ports = _container.attrs.get('NetworkSettings', None).get('Ports', None)
        if ports is not None:
            container_json['ports'] = ", ".join([
                (f"{v[0].get('HostPort')} -> {k}"
                 if len(v) == 2 and v[0].get('HostPort') == v[1].get('HostPort')
                 else
                 ", ".join([f"{each_binding.get('HostIp')}:{each_binding.get('HostPort')} -> {k}"
                           for each_binding in v])
                 )
                if v is not None else k
                for k, v in ports.items()
            ])

        return container_json

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return " "

    def print_out(self):
        for k, _container in self._loaded_containers.items():
            print(_container.id)
            print(_container.short_id, "-> ", _container.name, f" ({_container.image.tags[0]}): ", _container.status,
                  "\t Created at: ", Docker.convert_time(_container.attrs['Created']), " Ago")
            if _container.status == 'running':
                print("Up", Docker.convert_time(_container.attrs['State']['StartedAt']), end="")
                if 'Health' in _container.attrs['State']:
                    print(f" ({_container.attrs['State']['Health']['Status']})")
                else:
                    print()
            elif _container.status == 'exited':
                print(f"Exited ({_container.attrs['State']['ExitCode']})",
                      Docker.convert_time(_container.attrs['State']['StartedAt']), " Ago")
            # print(container.attrs['State']['FinishedAt'])

            port_bindings = _container.attrs['HostConfig']['PortBindings']
            extra_host = _container.attrs['HostConfig']['ExtraHosts']
            print('port bindings: ', port_bindings)
            print('extra host: ', extra_host)
            exposed_port = _container.attrs.get('Config', None).get('ExposedPorts', None)
            # if 'ExposedPorts' in _container.attrs['Config']:
            #     exposed_port = _container.attrs['Config']['ExposedPorts']
            print('exposed port: ', exposed_port)
            ports = _container.attrs['NetworkSettings']['Ports']
            print('ports: ', ports)
            # if port_bindings is not None:
            # print(container.attrs)
            print('============================================================================')

            # If it has ports (len(ports) > 0), then it will have the property of exposed ports,
            # if its ports has binding, then it will appear in port bindings (as well as exposed ports)

    @staticmethod
    def extract_image(_image):
        return _image.tags[0]

    @staticmethod
    def parse_container_iso_8601_date(date_str: str) -> datetime:
        return datetime.strptime(date_str[:-4], "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def convert_datetime_to_time_ago(to_date: datetime) -> str:
        now = datetime.now()
        assert now > to_date, "past date > now, how is it possible"
        delta_time = now - to_date
        seconds = delta_time.total_seconds()
        minutes = seconds / 60
        average_days_in_month = 365 / 12
        retval = f"{minutes} Minutes"
        if minutes > 60:
            hours = minutes / 60
            retval = f"{hours} Hours"
            if hours > 24:
                days = hours / 24
                retval = f"{days} Days"
                if 14 < days < average_days_in_month * 2:
                    weeks = days / 7
                    retval = f"{weeks} Weeks"
                elif average_days_in_month * 2 < days < 365:
                    months = days / average_days_in_month
                    retval = f"{months} Months"
                elif days > 365:
                    years = days / 365
                    retval = f"{years} Years"

        time, text = retval.split(' ')
        time = str(math.floor(float(time)))
        return time + " " + text

    @staticmethod
    def convert_time(iso_time: str) -> str:
        return Docker.convert_datetime_to_time_ago(Docker.parse_container_iso_8601_date(iso_time))


if __name__ == '__main__':
    client = Docker()
    print(client.load_all_containers())
