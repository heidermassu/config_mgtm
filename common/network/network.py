from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network import NetworkManagementClient

# Declare shared variables
resource_group_name = ''
vm_name = ''
disk_name = ''
snapshot_name = ''
public_ip_address = ''
ssh_user = ''
key_path = ''
subscription_id = ''
vm_inf = ''
stoping_commands = ''
sshconnection = ''
snap_skudisk = ''
new_disk_name = ''
new_vm_name = ''
vm_size =''
starting_commands = ''
nic_name = ''
location = ''
subnet_id = ''
ip_configuration_name = ''
private_ip_address_allocation = ''
vnetnet_id = ''
target_resource_group = ''

def initialize_variables(resource_group, vm, disk, snapshot, public_ip, user, key, subscriptionid, vminf, stop_commands, ssh, snapskudisk, newdisk_name, newvm_name, vmsize, start_commands, nicname, location, vnetnetid, subnetid, ipconfigurationname, privateipaddressallocation, targetresource_group):
    global resource_group_name, vm_name, disk_name, snapshot_name, subscription_id, public_ip_address, ssh_user, key_path, vm_inf, stoping_commands,sshconnection, snap_skudisk, starting_commands, nic_name
    resource_group_name = resource_group
    vm_name = vm
    disk_name = disk
    snapshot_name = snapshot
    public_ip_address = public_ip
    ssh_user = user
    key_path = key
    subscription_id = subscriptionid
    vm_inf = vminf
    stoping_commands = stop_commands
    sshconnection = ssh
    snap_skudisk = snapskudisk    
    new_disk_name = newdisk_name
    new_vm_name = newvm_name
    vm_size = vmsize
    starting_commands = start_commands
    nic_name = nicname
    location = location
    subnet_id = subnetid
    ip_configuration_name = ipconfigurationname
    private_ip_address_allocation = privateipaddressallocation
    vnetnet_id = vnetnetid
    target_resource_group = targetresource_group

def create_nic(targetresource_group, subscriptionid, nicname, location, vnetnetid, subnetid, ipconfigurationname, privateipaddressallocation):
    subscription_id = subscriptionid
    credential = DefaultAzureCredential()

    # Create a new NIC
    client = NetworkManagementClient(credential, subscription_id)
    nic = client.network_interfaces.begin_create_or_update(
        targetresource_group, nicname, {
            "location": location,
            "ip_configurations": [{
                "name": ipconfigurationname,
                'subnet': {'id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'.format(
                    subscriptionid, targetresource_group, vnetnetid, subnetid)
                },
                "private_ip_allocation_method": privateipaddressallocation
            }],
        }
    ).result()
    print(f"NIC '{nic.name}' created successfully.")

def nic_attach(targetresource_group, rg_vnet, resource_group, vm, newvm_name, subscriptionid, nicname, vnetnetid, subnetid, ipconfigurationname, privateipaddressallocation):
    subscription_id = subscriptionid
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Create Network Client
    client = NetworkManagementClient(credential, subscription_id)

    # Get the current VM
    current_vm = compute_client.virtual_machines.get(resource_group, vm)
    
    # Save the current NIC ID to detach later
    current_nic_id = current_vm.network_profile.network_interfaces[0].id

    # Create NIC object
    nic = client.network_interfaces.begin_create_or_update(
        targetresource_group, nicname, {
            "location": current_vm.location,
            "ip_configurations": [{
                "name": ipconfigurationname,
                'subnet': {'id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'.format(
                    subscriptionid, rg_vnet, vnetnetid, subnetid)
                },
                "private_ip_allocation_method": privateipaddressallocation
            }],
        }
    ).result()

    # ataching NEW NIC just created
    compute_client.virtual_machines.begin_create_or_update(
            resource_group, vm, {
                "location": current_vm.location,
                "network_profile": {
                    "network_interfaces": [
                        {
                            "id": nic.id,
                        }
                    ]
            }
            }
        ).result()  # Wait for the operation to complete

    print(f"NIC {nicname} attached to VM {vm} successfully!")

    # Return the ID of the detached NIC for later use
    #return current_nic_id

    # ataching old NIC in other vm
    compute_client.virtual_machines.begin_create_or_update(
            targetresource_group, newvm_name, {
                "location": current_vm.location,
                "network_profile": {
                    "network_interfaces": [
                        {
                            "id": current_nic_id,
                        }
                    ]
            }
            }
        ).result()  # Wait for the operation to complete

    print(f"NIC {current_nic_id} attached to VM {newvm_name} successfully!")