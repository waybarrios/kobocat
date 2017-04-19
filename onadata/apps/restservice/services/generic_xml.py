import requests

from onadata.apps.restservice.RestServiceInterface import RestServiceInterface


class ServiceDefinition(RestServiceInterface):
    id = u'xml'
    verbose_name = u'XML POST'

    def send(self, url, parsed_instance):
        instance = parsed_instance.instance
        headers = {"Content-Type": "application/xml"}
        requests.post(url, instance.xml, headers=headers)
