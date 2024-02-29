from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption

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

def initialize_variables(resource_group, vm, disk, snapshot, public_ip, user, key, subscriptionid, vminf, stop_commands, ssh, snapskudisk, newdisk_name, newvm_name, vmsize, start_commands, nicname):
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


def create_vm_snapshot(resource_group, vm, disk, snapshot, subscriptionid, vminf, snapskudisk):
    subscription_id = subscriptionid
    credential = DefaultAzureCredential()

    compute_client = ComputeManagementClient(credential, subscription_id)

    # Get the VM
    vminf = compute_client.virtual_machines.get(resource_group, vm)

    # Get the OS disk ID
    os_disk_id = vminf.storage_profile.os_disk.managed_disk.id

    if os_disk_id:
        #sku = snapskudisk
        # Create snapshot
        snapshot_creation_result = compute_client.snapshots.begin_create_or_update(
            resource_group,
            snapshot,
            {
                'location': vminf.location,
                'creation_data': {
                    'create_option': DiskCreateOption.copy,
                    'source_resource_id': os_disk_id
                    #'os_disk_id': os_disk_id,
                    },
                'sku': {'name': snapskudisk}
            }
        ).result()

        print(f"Snapshot '{snapshot}' created successfully.")

    else:
        print(f"Could not find the OS disk ID for VM '{vm_name}'.")

def create_disk_from_snap(resource_group, vm, disk, snapshot, subscriptionid, vminf, snapskudisk):
    subscription_id = subscriptionid
    credential = DefaultAzureCredential()

    compute_client = ComputeManagementClient(credential, subscription_id)

    # Get the VM
    vminf = compute_client.virtual_machines.get(resource_group, vm)

    # Get the OS disk ID
    os_disk_id = vminf.storage_profile.os_disk.managed_disk.id

    if os_disk_id:
        #sku = snapskudisk
        # Create snapshot
        snapshot_creation_result = compute_client.snapshots.begin_create_or_update(
            resource_group,
            snapshot,
            {
                'location': vminf.location,
                'creation_data': {
                    'create_option': DiskCreateOption.copy,
                    'source_resource_id': os_disk_id
                    #'os_disk_id': os_disk_id,
                    },
                'sku': {'name': snapskudisk}
            }
        ).result()

        # Create disk from snapshot
        disk_creation_result = compute_client.disks.begin_create_or_update(
            resource_group,
            disk_name + disk,
            {
                'location': vminf.location,
                'creation_data': {
                    'create_option': DiskCreateOption.copy,
                    'source_resource_id': snapshot_creation_result.id
                },
                'sku': {'name': snapskudisk}
            }
        ).result()
        print(f"Snapshot '{snapshot}' created successfully.")
        print(f"Disk from snapshot '{disk_name}-snapshot' created successfully.")
    else:
        print(f"Could not find the OS disk ID for VM '{vm_name}'.")