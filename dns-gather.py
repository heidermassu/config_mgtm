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
    public_ip = nic.ip_configurations[0].public_ip_address.ip_address if nic.ip_configurations[0].public_ip_address else "N/A"
    return private_ip, public_ip

# Virtual Machines
vm_sheet = workbook.create_sheet("Virtual Machines")
vm_sheet.append(["Resource Group", "Host", "Private IP", "Public IP"])
for rg in resource_client.resource_groups.list():
    for vm in compute_client.virtual_machines.list(rg.name):
        for nic_reference in vm.network_profile.network_interfaces:
            nic = network_client.network_interfaces.get(rg.name, nic_reference.id.split('/')[-1])
            private_ip, public_ip = get_ip_addresses(nic)
            vm_sheet.append([rg.name, vm.name, private_ip, public_ip])

# App Services
app_services_sheet = workbook.create_sheet("App Services")
app_services_sheet.append(["Resource Group", "Web App", "Default Domain", "Custom Domains"])
for rg in resource_client.resource_groups.list():
    for site in web_client.web_apps.list_by_resource_group(rg.name):
        app_services_sheet.append([rg.name, site.name, site.default_host_name, ", ".join(site.enabled_host_names)])

# Save the workbook
workbook.save("azure_resources.xlsx")
