from common.vm.vm import initialize_variables, create_snapshot_os_disk

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption, DiskCreateOptionTypes, DataDisk
import time

#variables
subscription_id = '' # Replace with the subscription Id where is based the VM
resource_group_name = 'manual' # Replace with the RG regarding the source VM
vm = 'vm1' # Replace with the RG regarding the where you want to create the new VM
targetresource_group = 'aut' # Replace with the RG regarding the where you want to create the new VM
snapshot = 'snap-vm1-test1' # Snapshot name going to be created
snap_skudisk= 'Premium_LRS' # You have only 2 choise ## Premium_LRS,Standard_LRS


## going to create snapshot of os disk only

# Connect to Azure and get VM information
credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential, subscription_id)

# Get VM information
vm_inf = compute_client.virtual_machines.get(resource_group_name, vm)

create_snapshot_os_disk(targetresource_group, resource_group_name, vm, snapshot, subscription_id, vm_inf, snap_skudisk)
