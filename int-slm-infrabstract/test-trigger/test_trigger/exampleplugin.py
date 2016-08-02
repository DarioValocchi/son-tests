"""
Created by Manuel Peuster <manuel@peuster.de>

This is a stupid MANO plugin used for testing.
"""

import logging
import json
import time
import sys
import os
import yaml
import uuid

sys.path.append("../son-mano-base")
from sonmanobase.plugin import ManoBasePlugin

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("plugin:example-plugin-1")
LOG.setLevel(logging.DEBUG)


class DemoPlugin1(ManoBasePlugin):
    """
    This is a very simple example plugin to demonstrate
    some APIs.

    It does the following:
    1. registers itself to the plugin manager
    2. waits some seconds
    3. requests a list of active plugins from the plugin manager and prints it
    4. de-registers itself
    """

    def __init__(self):
        self.correlation_id = str(uuid.uuid4())
        # call super class to do all the messaging and registration overhead
        super(self.__class__, self).__init__(version="0.1-dev")

    def __del__(self):
        super(self.__class__, self).__del__()

    def declare_subscriptions(self):
        """
        Declare topics to listen.
        """
        # We have to call our super class here
        super(self.__class__, self).declare_subscriptions()
        # Examples to demonstrate how a plugin can listen to certain events:
        self.manoconn.register_async_endpoint(
            self._on_example_request,  # call back method (expected to return a response message)
            "example.plugin.*.request")
        self.manoconn.register_notification_endpoint(
            self._on_example_notification,  # call back method
            "example.plugin.*.notification")

        #Faking the IA, currently disabled.
#        self.manoconn.register_notification_endpoint(
#            self.on_service_deploy_request,
#            "infrastructure.service.deploy")
#
        # Activate this to sniff and print all messages on the broker
#        self.manoconn.subscribe(self.callback_print, "infrastructure.service.deploy")

        #We need to receive all messages from the slm intended for the gk
        self.manoconn.subscribe(self.on_slm_messages, "service.instances.create")

        self.manoconn.subscribe(self.on_list, "infrastructure.management.compute.list")
        #self.manoconn.subscribe(self.on_infrastructure_adaptor_reply, "infrastructure.service.remove")

    def run(self):
        """
        Plugin logic. Does nothing in our example.
        """
        print('corr_id:'+self.correlation_id)
        time.sleep(360)
        print('Timeout')
        os._exit(1)

    def on_registration_ok(self):
        """
        Event that is triggered after a successful registration process.
        """
        LOG.info("Registration OK.")

    def on_lifecycle_start(self, ch, method, properties, message):
        super(self.__class__, self).on_lifecycle_start(ch, method, properties, message)

        #We don't add VIM(s) in integration environment. The IA is configured
        # vim_message = json.dumps({'tenant':'iMinds', 'wr_type' : 'compute', 'vim_type': 'Mock', 'vim_address' : 'http://localhost:9999', 'username' : 'Eve', 'pass':'Operator'})
	#self.manoconn.call_async(self.on_infrastructure_adaptor_reply, 'infrastructure.management.compute.add',vim_message)
        #time.sleep(3)

        #At deployment, this plugin generates a service request, identical to how the GK will do it in the future.
        message = self.createGkNewServiceRequestMessage()
        #self.correlation_id = uuid.uuid4().hex
        self.manoconn.call_async(
                        self.on_slm_messages,
                        "service.instances.create",
                        message,
                        content_type="application/yaml",
                        correlation_id=self.correlation_id)

    def on_infrastructure_adaptor_reply(self, ch, method, properties, message):

        print('infra response: ' + str(json.loads(str(message, "utf-8"))))

    def on_slm_messages(self, ch, method, properties, message):
        """
        Printing response from the SLM to the GK on all messages.
        """
        msg = yaml.load(message)

        print("RESPONSE FROM GK START")
        print(msg)
        print("RESPONSE FROM GK END")
        if 'error' in msg.keys() and (properties.correlation_id == self.correlation_id):
            if msg['error'] != None:
                print(msg['error'])
                os._exit(1)
        if 'status' in msg.keys() and (properties.correlation_id == self.correlation_id):
            if msg['status'] == 'READY':
                os._exit(0)

    def removeService(self, msg):
        id = msg['nsr']['id']
        print('removing the deployed service')
        vim_message = json.dumps({'instance_uuid':id,'vim_uuid':'1111-22222222-33333333-4444'})
        print('sending message:',vim_message)
        self.manoconn.call_async(self.on_infrastructure_adaptor_reply, 'infrastructure.service.remove',vim_message)
        time.sleep(30)



    def callback_print(self, ch, method, properties, message):

        print('correlation_id: ' + str(properties.correlation_id))
        print('message: ' + str(message))

    def on_service_deploy_request(self, ch, method, properties, message):
        """
        IA faking
        """

        LOG.debug("request from SLM for IA: %r" % str(yaml.load(message)))
        if properties.app_id != 'son-plugin.DemoPlugin1':
            self.manoconn.notify("infrastructure.service.deploy", self.createInfrastructureAdapterResponseMessage(), content_type='application/yaml', correlation_id=properties.correlation_id)

    def _on_example_request(self, ch, method, properties, message):
        """
        Only used for the examples.
        """
        print("Example message: %r " % message)
        return json.dumps({"content" : "my response"})

    def _on_example_request_response(self, ch, method, properties, message):
        """
        Only used for the examples.
        """
        print("Example message: %r " % message)

    def _on_example_notification(self, ch, method, properties, message):
        """
        Only used for the examples.
        """
        print("Example message: %r " % message)

    def createGkNewServiceRequestMessage(self):
        """
        This method helps creating messages for the service request packets.
        """

        path_descriptors = 'test_descriptors/'
    	#import the nsd and vnfds that form the service	
        nsd_descriptor   = open(path_descriptors + 'sonata-demo.yml','r')
        vnfd1_descriptor = open(path_descriptors + 'firewall-vnfd.yml','r')
        vnfd2_descriptor = open(path_descriptors + 'iperf-vnfd.yml','r')
        vnfd3_descriptor = open(path_descriptors + 'tcpdump-vnfd.yml','r')

        service_request = {'NSD': yaml.load(nsd_descriptor), 'VNFD1': yaml.load(vnfd1_descriptor), 'VNFD2': yaml.load(vnfd2_descriptor), 'VNFD3': yaml.load(vnfd3_descriptor)}

        return yaml.dump(service_request)

    def createInfrastructureAdapterResponseMessage(self):
        path_descriptors = 'test_records/'

        ia_nsr = yaml.load(open(path_descriptors + 'ia-nsr.yml','r'))

        return str(ia_nsr)

    def on_list(self, ch, method, properties, message):
        print(properties)


def main():
    # reduce log level to have a nice output for demonstration
    # reduce messaging log level to have a nicer output for this plugin
    logging.getLogger("son-mano-base:messaging").setLevel(logging.INFO)
    logging.getLogger("son-mano-base:plugin").setLevel(logging.INFO)
    DemoPlugin1()

if __name__ == '__main__':
    main()
