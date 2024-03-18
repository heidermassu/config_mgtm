import csv
from openpyxl import Workbook
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient

def get_vm_dns_info(network_client, compute_client, resource_group_name, vm_name):
    
    vm = compute_client.virtual_machines.get(resource_group_name, vm_name)

    private_ip_id = vm.network_profile.network_interfaces[0].id
    private_ip_interface = network_client.network_interfaces.get(resource_group_name, private_ip_id.split('/')[-1])
    private_ip_address = private_ip_interface.ip_configurations[0].private_ip_address

    public_ip_id = vm.network_profile.network_interfaces[0].id
    public_ip_interface = network_client.network_interfaces.get(resource_group_name, public_ip_id.split('/')[-1])
    public_ip_address = public_ip_interface.ip_configurations[0].public_ip_address

    return private_ip_address, public_ip_address

def get_resource_info(resource_client):
    resource_info = []
    for resource in resource_client.resources.list():
        resource_type = resource.type.split('/')[-1]
        resource_name = resource.name
        resource_group = resource.id.split('/')[4]
        location = resource.location
        resource_info.append([resource_type, resource_name, resource_group, location])
    return resource_info

def main():
    subscription_id = 'a6cc1a53-c242-42f9-aa16-15a377d21069'
    compute_client = ComputeManagementClient(DefaultAzureCredential(), subscription_id)
    resource_client = ResourceManagementClient(DefaultAzureCredential(), subscription_id)

    # Get resource information
    #resource_info = get_resource_info(resource_client)
    resource_client = ResourceManagementClient(DefaultAzureCredential(), subscription_id)

    # Create a workbook and sheets for each service type
    workbook = Workbook()
    vm_sheet = workbook.create_sheet(title="Virtual Machines")
    vm_sheet.append(['VM Name', 'Resource Group', 'Private IP', 'Public IP', 'Internal DNS', 'Local Resolution'])

    # Populate VMs sheet with DNS information
    for vm_info in resource_client:
        if vm_info[0] == 'Microsoft.Compute/virtualMachines':
            vm_name = vm_info[1]
            resource_group_name = vm_info[2]
            private_ip, public_ip = get_vm_dns_info(compute_client, resource_group_name, vm_name)
            ## For simplicity, let's assume local resolution is always done
            vm_sheet.append([vm_name, resource_group_name, private_ip, public_ip, 'Local Resolution'])

    # Save the workbook
    workbook.save(filename='azure_dns_info.xlsx')



def test():
    subscription_id = 'a6cc1a53-c242-42f9-aa16-15a377d21069'
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(DefaultAzureCredential(), subscription_id)
    resource_client = ResourceManagementClient(DefaultAzureCredential(), subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)


     # Get resource information
    #resource_info = get_resource_info(resource_client)
    for resources in resource_client.resources.list():
        #print(f"test: {resources}")
        #resource_type = resources
        #print(f"test: {resource_type}")
        if resources.type == 'Microsoft.Compute/virtualMachines':
            vm_name = resources.name
            resource_group_name = resources.id
            location = resources.location
            test = get_vm_dns_info(network_client, compute_client, resource_group_name, vm_name)
            print(f"test: {test}")
if __name__ == "__main__":
    test()
