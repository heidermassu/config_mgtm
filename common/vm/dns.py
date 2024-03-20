from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from openpyxl import Workbook
from azure.core.exceptions import ResourceNotFoundError
from kubernetes import client, config
from azure.mgmt.containerservice import ContainerServiceClient

# Variables
network_client = ''

# Function to get DNS info with error handling
def get_dns_info(vm, nic_ref, network_client):
    custom_dns = "N/A"
    private_dns = "N/A"
    dns_servers = "N/A"

    try:
        # Retrieve network interface
        nic = network_client.network_interfaces.get(nic_ref.split('/')[4], nic_ref.split('/')[-1])

        # Retrieve custom DNS
        if nic.dns_settings and nic.dns_settings.internal_domain_name_suffix:
            custom_dns = f"{vm.name}.{nic.dns_settings.internal_domain_name_suffix}"
        
        # Retrieve private DNS
        if nic.dns_settings and nic.dns_settings.dns_servers:
            private_dns = nic.dns_settings.dns_servers
        
        # Retrieve associated virtual network
        subnet_id = nic.ip_configurations[0].subnet.id
        subnet_parts = subnet_id.split('/')
        resource_group_name = subnet_parts[4]
        virtual_network_name = subnet_parts[8]
        virtual_network = network_client.virtual_networks.get(resource_group_name, virtual_network_name)

        if virtual_network.dhcp_options and virtual_network.dhcp_options.dns_servers:
            dns_servers = virtual_network.dhcp_options.dns_servers

        return custom_dns, private_dns, dns_servers

    except ResourceNotFoundError as e:
        print(f"Resource not found while retrieving DNS info: {e}")
        # Return None if any resource is not found
        return None

    except Exception as e:
        print(f"Error occurred while retrieving DNS info: {e}")
        # Log the error or handle it as needed
        return None
