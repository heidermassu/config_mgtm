from common.vm.vm import create_vm_from_snap, deallocating_vm, delete_vm, attach_existing_managed_disks


from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential


subscriptionid = ''
targetresource_group = 'Python-Poc' #resource group where going to be create the new VM. Could be same RG the old but necessary delete the old one.
resource_group= 'Python-Poc' # resource group where live the vm that have to be restored
vm = 'heider-vm01' # vm name that have to be restored
disk ='disk-from-snap4' #name of the os disk going to be created for the new VM
disk_managed_name = ['heider-vm01_DataDisk_2', 'heiderDataDisk_1'] # In case there are managed disks attached fill with the names ['disk'', 'disk2']
snapskudisk = 'Premium_LRS' # You have only 2 choise ## Premium_LRS,Standard_LRS
snapshot ='snap-heider-vm04' #name of the snapshot going to be created
newvm_name = 'heider-vm01' # Name of the new vm going to be created. Could be same name but the flag 'del_vm' have to be 'True' otherwise will get error due to have vm with same name 
vmsize = 'Standard_D2s_v3' # Replace with the desired VM size
securityType = 'Trustedlaunch' # Trustedlaunch or Standard
del_vm = True #True or False.  True going to delete vm (used when you want create with same name same RG.) False going to leave the old VM as deallocated
attach_nic = True #True or False
nsg_name = 'heider-vm01-nsg' #This is the NSG going to be either attached in the new vm or created if do not have
nic_name = 'heider-vm01647' #Should be filled only if 'attach_nic' is 'True' otherwise will not have impact. this is the NIC going to be attached in the new vm
rg_vnet = 'Python-Poc' # RG where is the VNET
vnetnetid = 'heider-vm01-vnet' #VNET ID where is the NIC that want to be attached. Must be same one was in the old VM
subnetid = 'default' #SUBNET ID where is the NIC that want to be attached. Must be same one was in the old VM


credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential, subscriptionid)

# Get VM information going to be deleted
vm_inf = compute_client.virtual_machines.get(resource_group, vm)

# Going to deallocate VM settled in the variables
deallocating_vm(rg_vnet, vm, subscriptionid)
if del_vm:
    delete_vm (resource_group, vm, subscriptionid, vm_inf)

create_vm_from_snap(securityType, nsg_name, attach_nic, nic_name, targetresource_group, rg_vnet, resource_group, disk, vnetnetid, subnetid, snapshot, subscriptionid, snapskudisk, newvm_name, vmsize)
#deallocating_vm(targetresource_group, newvm_name, subscriptionid)
attach_existing_managed_disks(targetresource_group, resource_group, newvm_name, subscriptionid, disk_managed_name)

