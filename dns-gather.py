from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from openpyxl import Workbook
from azure.core.exceptions import ResourceNotFoundError

# Initialize Azure credentials
credentials = DefaultAzureCredential()
subscription_id = 'a6cc1a53-c242-42f9-aa16-15a377d21069'

# Initialize Azure clients
compute_client = ComputeManagementClient(credentials, subscription_id)
network_client = NetworkManagementClient(credentials, subscription_id)
web_client = WebSiteManagementClient(credentials, subscription_id)
resource_client = ResourceManagementClient(DefaultAzureCredential(), subscription_id)

# Create a new Excel workbook
workbook = Workbook()

# Function to get IP addresses from a network interface
def get_ip_addresses(nic):
    private_ip = nic.ip_configurations[0].private_ip_address
    if nic.ip_configurations[0].public_ip_address:
        public_ip_id = nic.ip_configurations[0].public_ip_address.id
        public_ip_rg = public_ip_id.split('/')[4]  # Extracting resource group from resource ID
        public_ip = network_client.public_ip_addresses.get(public_ip_rg, public_ip_id.split('/')[-1]).ip_address
    else:
        public_ip = "N/A"  # Assign a default value when there's no public IP
    return private_ip, public_ip

# Function to get DNS info with improved error handling
def get_dns_info(vm, nic_ref):
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


# Virtual Machines
vm_sheet = workbook.create_sheet("Virtual Machines")
vm_sheet.append(["Resource Group", "Host", "Private IP", "Public IP", "Internal Domain Name Suffix", "Private DNS", "DNS Servers"])
for rg in resource_client.resource_groups.list():
    for vm in compute_client.virtual_machines.list(rg.name):
        for nic_reference in vm.network_profile.network_interfaces:
            try:
                nic = network_client.network_interfaces.get(rg.name, nic_reference.id.split('/')[-1])
                dns_info = get_dns_info(vm, nic.id)
                if dns_info is not None:
                    custom_dns, private_dns, dns_servers = dns_info
                else:
                    # Assign default values if get_dns_info() returns None
                    custom_dns, private_dns, dns_servers = "N/A", "N/A", "N/A"
                
                private_ip, public_ip = get_ip_addresses(nic)
                
                # Convert DNS servers to a string
                dns_servers_str = ", ".join(dns_servers) if dns_servers != "N/A" else "N/A"
                
                vm_sheet.append([rg.name, vm.name, private_ip, public_ip, custom_dns, private_dns, dns_servers_str])

            except ResourceNotFoundError as e:
                print(f"Resource not found while retrieving NIC: {e}")
                # Continue to the next iteration
                continue

            except Exception as e:
                print(f"Error occurred while retrieving NIC: {e}")
                # Log the error or handle it as needed
                continue
# App Services
app_services_sheet = workbook.create_sheet("App Services")
app_services_sheet.append(["Resource Group", "App Services", "Default Domain", "Custom Domains"])
for rg in resource_client.resource_groups.list():
    for site in web_client.web_apps.list_by_resource_group(rg.name):
        app_services_sheet.append([rg.name, site.name, site.default_host_name, ", ".join(site.enabled_host_names)])

# Save the workbook
workbook.save("azure_resources.xlsx")
