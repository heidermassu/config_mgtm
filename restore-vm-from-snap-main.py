from common.vm.vm import create_vm_from_snap, deallocating_vm, delete_vm
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential

targetresource_group = 'Python-Poc'
rg_vnet = 'Python-Poc'
resource_group= 'Python-Poc'
disk ='disk-from-snap3'
vnetnetid = 'heider-vm01-vnet'
subnetid = 'default'
snapshot ='snap-heider-vm01'
subscriptionid = 'a6cc1a53-c242-42f9-aa16-15a377d21069'
snapskudisk = 'Premium_LRS'
newvm_name = 'heider-vm01'
vmsize = 'Standard_D2s_v3'
vm = 'heider-vm01'

credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential, subscriptionid)

# Get VM information
vm_inf = compute_client.virtual_machines.get(resource_group, vm)

# Going to deallocate VM settled in the variables
deallocating_vm(rg_vnet, vm, subscriptionid)
delete_vm (resource_group, vm, subscriptionid, vm_inf)
create_vm_from_snap(targetresource_group, rg_vnet, resource_group, disk, vnetnetid, subnetid, snapshot, subscriptionid, snapskudisk, newvm_name, vmsize)


