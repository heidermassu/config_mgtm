from common.vm.vm import create_vm_from_snap, deallocating_vm, delete_vm, attach_existing_managed_disks


from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential


subscriptionid = ''
targetresource_group = 'Python-Poc'
resource_group= 'Python-Poc'
vm = 'heider-vm01'
disk ='disk-from-snap4'
snapskudisk = 'Premium_LRS'
snapshot ='snap-heider-vm04'
newvm_name = 'heider-vm01'
vmsize = 'Standard_D2s_v3'
securityType = 'Trustedlaunch' # Trustedlaunch or Standard
del_vm = False #True or False.  True going to delete vm (used when you want create with same name same RG.) False going to leave the old VM as deallocated
attach_nic = True #True or False
attach_nsg = True #True or False.  True going to attach the nsg mentioned in nsg_name
nsg_name = '' #Should be filled only if attach_nsg is True otherwise will not have impact. This is the NSG going to be attached in the new vm
nic_name = 'heider-vm0159' #Should be filled only if 'attach_nic' is 'True' otherwise will not have impact. this is the NIC going to be attached in the new vm
rg_vnet = 'Python-Poc'
vnetnetid = 'heider-vm01-vnet'
subnetid = 'default'


credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential, subscriptionid)

# Get VM information going to be deleted
vm_inf = compute_client.virtual_machines.get(resource_group, vm)

# Going to deallocate VM settled in the variables
#deallocating_vm(rg_vnet, vm, subscriptionid)
if del_vm:
    delete_vm (resource_group, vm, subscriptionid, vm_inf)

#create_vm_from_snap(securityType, attach_nsg, attach_nic, nic_name, targetresource_group, rg_vnet, resource_group, disk, vnetnetid, subnetid, snapshot, subscriptionid, snapskudisk, newvm_name, vmsize)
#deallocating_vm(targetresource_group, newvm_name, subscriptionid)
attach_existing_managed_disks(targetresource_group, resource_group, newvm_name, subscriptionid, newvm_name)

