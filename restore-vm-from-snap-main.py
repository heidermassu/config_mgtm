from common.vm.vm import create_vm_from_snap

targetresource_group = ''
rg_vnet = ''
resource_group= ''
disk =''
vnetnetid = ''
subnetid = ''
snapshot =''
subscriptionid = ''
snapskudisk = ''
newvm_name = ''
vmsize = ''

create_vm_from_snap(targetresource_group, rg_vnet, resource_group, disk, vnetnetid, subnetid, snapshot, subscriptionid, snapskudisk, newvm_name, vmsize)