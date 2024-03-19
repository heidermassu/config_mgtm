from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from openpyxl import Workbook

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


# Function to get private DNS information
#def get_private_dns_info(vm, nic_ref):
#    internal_fqdn = []
#    internal_dns_name_label = []
#    applied_dns_servers = []
#    internal_domain_name_suffix = []
#    nic = network_client.network_interfaces.get(nic_ref.split('/')[4], nic_ref.split('/')[-1])
#    if nic.dns_settings:
#        internal_fqdn.append(nic.dns_settings.internal_fqdn)
#        internal_dns_name_label.append(nic.dns_settings.internal_dns_name_label)
#        applied_dns_servers.append(nic.dns_settings.applied_dns_servers)
#        internal_domain_name_suffix.append(nic.dns_settings.internal_domain_name_suffix)
#    combined_info = internal_fqdn + internal_dns_name_label + applied_dns_servers + internal_domain_name_suffix
#    combined_info = [str(info) for info in combined_info if info is not None]
#    return ", ".join(combined_info) if combined_info else "N/A"
##def get_dns_info(vm, nic_ref):
##    custom_dns = "N/A"
##    private_dns = "N/A"
##    dns_servers = "N/A"
##
##    # Retrieve network interface
##    nic = network_client.network_interfaces.get(nic_ref.split('/')[4], nic_ref.split('/')[-1])
##
##    # Retrieve custom DNS
##    if nic.dns_settings and nic.dns_settings.internal_domain_name_suffix:
##        custom_dns = f"{vm.name}.{nic.dns_settings.internal_domain_name_suffix}"
##    
##    # Retrieve private DNS
##    if nic.dns_settings and nic.dns_settings.dns_servers:
##        private_dns = nic.dns_settings.dns_servers
##    
##    # Retrieve associated virtual network
##    virtual_network_id = nic.ip_configurations[0].subnet.id.split('/')[6]
##    virtual_network = network_client.virtual_networks.get(nic_ref.split('/')[4], virtual_network_id)
##
##    if virtual_network.dhcp_options and virtual_network.dhcp_options.dns_servers:
##        dns_servers = virtual_network.dhcp_options.dns_servers
##
##    return custom_dns, private_dns, dns_servers

def get_dns_info(vm, nic_ref):
    custom_dns = "N/A"
    private_dns = "N/A"
    dns_servers = "N/A"

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


# Virtual Machines
#vm_sheet = workbook.create_sheet("Virtual Machines")
#vm_sheet.append(["Resource Group", "Host", "Private IP", "Public IP", "Private DNS"])
#for rg in resource_client.resource_groups.list():
#    for vm in compute_client.virtual_machines.list(rg.name):
#        for nic_reference in vm.network_profile.network_interfaces:
#            nic = network_client.network_interfaces.get(rg.name, nic_reference.id.split('/')[-1])
#            private_ip, public_ip = get_ip_addresses(nic)
#            custom_dns, private_dns, dns_servers = get_dns_info(vm, nic.id)
#            #print (custom_dns, private_dns, nic.ip_configurations)
#            vm_sheet.append([rg.name, vm.name, private_ip, public_ip, custom_dns, private_dns, dns_servers])
#

# Virtual Machines
vm_sheet = workbook.create_sheet("Virtual Machines")
vm_sheet.append(["Resource Group", "Host", "Private IP", "Public IP", "Custom DNS", "Private DNS", "DNS Servers"])
for rg in resource_client.resource_groups.list():
    for vm in compute_client.virtual_machines.list(rg.name):
        for nic_reference in vm.network_profile.network_interfaces:
            nic = network_client.network_interfaces.get(rg.name, nic_reference.id.split('/')[-1])
            private_ip, public_ip = get_ip_addresses(nic)
            custom_dns, private_dns, dns_servers = get_dns_info(vm, nic.id)
            
            # Convert DNS servers to a string
            dns_servers_str = ", ".join(dns_servers) if dns_servers != "N/A" else "N/A"
            
            vm_sheet.append([rg.name, vm.name, private_ip, public_ip, custom_dns, private_dns, dns_servers_str])


# App Services
app_services_sheet = workbook.create_sheet("App Services")
app_services_sheet.append(["Resource Group", "App Services", "Default Domain", "Custom Domains"])
for rg in resource_client.resource_groups.list():
    for site in web_client.web_apps.list_by_resource_group(rg.name):
        app_services_sheet.append([rg.name, site.name, site.default_host_name, ", ".join(site.enabled_host_names)])

# Save the workbook
workbook.save("azure_resources.xlsx")
