from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.network import NetworkManagementClient
#from azure.mgmt.compute.models import DiskCreateOption, DiskCreateOptionTypes, VirtualMachineDataDisk
from azure.mgmt.compute.models import DataDisk, DiskCreateOption, DiskCreateOptionTypes, DataDisk

import paramiko
import socket

# Declare shared variables. The values comes from the main script
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
ssh_password = ''
target_resource_group = ''

def initialize_variables(resource_group, vm, disk, snapshot, public_ip, user, key, subscriptionid, vminf, stop_commands, ssh, snapskudisk, newdisk_name, newvm_name, vmsize, start_commands, nicname, location, vnetnetid, subnetid, ipconfigurationname, privateipaddressallocation, sshpassword, targetresource_group):
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
    ssh_password = sshpassword
    target_resource_group = targetresource_group

def create_snapshot_os_disk(targetresource_group, resource_group, vm, snapshot, subscriptionid, vminf, snapskudisk):
 ### This function aiming to:
    ## Create a snapshot of the OS disk lives in the VM mentioned in the variable 'vm_name';

    subscription_id = subscriptionid
    credential = DefaultAzureCredential()

    compute_client = ComputeManagementClient(credential, subscription_id)

    # Get the VM
    vminf = compute_client.virtual_machines.get(resource_group, vm)
    # Get the OS disk ID
    os_disk_id = vminf.storage_profile.os_disk.managed_disk.id
    
   
    if os_disk_id:
        # Create snapshot
        snapshot_creation_result = compute_client.snapshots.begin_create_or_update(
            targetresource_group,
            snapshot,
            {
                'location': vminf.location,
                'creation_data': {
                    'create_option': DiskCreateOption.copy,
                    'source_resource_id': os_disk_id
                },
                'sku': {'name': snapskudisk}
            }
        )
        return snapshot_creation_result  # Return the asynchronous operation

    return None  # Return None if there is no OS disk ID

def create_snap_and_vm(targetresource_group, rg_vnet, resource_group, vm, disk, vnetnetid, subnetid, snapshot, subscriptionid, vminf, snapskudisk, new_diskname, newvm_name, vmsize):
### This function aiming to:
    ## Create a snapshot of the OS disk lives in the VM mentioned in the variable 'vm_name';
    ## create a new disk from this snapshot;
    ## Create new a NIC in the same VNET/Sbunet of VM mentioned in the variable 'vm_name'
    ## 

    subscription_id = subscriptionid
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Get the VM
    vminf = compute_client.virtual_machines.get(resource_group, vm)
    # Get the OS disk ID
    os_disk_id = vminf.storage_profile.os_disk.managed_disk.id
   
    if os_disk_id:
        # Create snapshot
        snapshot_creation_result = create_snapshot_os_disk (targetresource_group, resource_group, vm, snapshot, subscriptionid, vminf, snapskudisk).result()

        # Create disk from snapshot
        disk_creation_result = compute_client.disks.begin_create_or_update(
            targetresource_group,
            disk,
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
        print(f"Disk from snapshot '{snapshot_creation_result.name}' created successfully.")

        # Create a new NIC
        new_nic_params = {
            'location': vminf.location,
            'ip_configurations': [{
                'name': 'ipconfig1',
                'subnet': {
                    'id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'.format(
                        subscription_id, rg_vnet, vnetnetid, subnetid)
                }
            }]
        }

        network_client = NetworkManagementClient(credential, subscription_id)
        new_nic = network_client.network_interfaces.begin_create_or_update(
            targetresource_group,
            f"nic-{newvm_name}",
            new_nic_params
        ).result()

        
        #new_nic = create_nic (resource_group, vm, subscriptionid, vminf, newvm_name)
        print(f"NIC '{new_nic.name}' created successfully.")


        # Create a new VM from the disk
        vm_creation_params = compute_client.virtual_machines.begin_create_or_update(
            targetresource_group,
            newvm_name,
            {
                'location': vminf.location,
                'storage_profile': {
                    'os_disk': {
                        'os_type': 'Linux',
                        'create_option': DiskCreateOption.attach,
                        'managed_disk': {
                            'id': disk_creation_result.id #, 'storage_account_type': snapskudisk # Specify the appropriate storage account type
                        }
                    }
                },
                'hardware_profile': {
                    'vm_size': vmsize
                },
                'network_profile': {
                    'network_interfaces': [{
                        'id': new_nic.id
                    }]
                },
                "securityProfile": {
                    #"uefiSettings": {
                    #"secureBootEnabled": True,
                    #"vTpmEnabled": True
                    #},
                    "securityType": "Standard" # Trustedlaunch or Standard
                }
        }).result()
        #compute_client.virtual_machines.create_or_update(resource_group, newvm_name, vm_creation_params)
        print(f"VM '{newvm_name}' created successfully from the disk.")
    else:
        print(f"Could not find the OS disk ID for VM '{vm_name}'.")

def deallocating_vm(resource_group, vm, subscriptionid):   
### This function aiming to:
    ## Deallocate the VM mentioned in the variable 'vm_name';

    subscription_id = subscriptionid
    credential = DefaultAzureCredential()

    compute_client = ComputeManagementClient(credential, subscription_id)
    try:
        print("Deallocating VM...")
        compute_client.virtual_machines.begin_deallocate(resource_group, vm).wait()
        print("VM deallocated successfully.")
    except Exception as e:
        print(f"Error deallocating VM: {e}")

def get_vm_status(vm_client, resource_group, vm):
### This function aiming to:
    ## Get the VM status of the VM mentioned in the variable 'vm_name';

    vm_status = vm_client.virtual_machines.get(resource_group, vm, expand='instanceView').instance_view.statuses[1].display_status
    return vm_status

def start_vm_created(resource_group, subscriptionid, newvm_name):
### This function aiming to:
    ## Start the VM is mentioned in the variable new_vm_name
    subscription_id = subscriptionid
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    try:
        print(f"starting VM {newvm_name}")
        compute_client.virtual_machines.begin_start(resource_group, newvm_name).wait()
        print(f"VM '{newvm_name}' started successfully.")
    except Exception as e:
        print(f"Error starting VM: {e}")

def execute_ssh_commands_stop(ssh, stop_commands):
# SSH into the VM and execute commands to stop services
    for command in stop_commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        print(f"Command: {command}")
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

def execute_ssh_commands_start(ssh, start_commands):
# SSH into the VM and execute commands to start services
    for command in start_commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        print(f"Command: {command}")
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))

def ssh_into_vm(pip, sshuser, keypath=None, sshpassword=None, timeout=10):
# SSH into the VM 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if keypath:
            private_key = paramiko.RSAKey(filename=keypath)
            ssh.connect(pip, username=sshuser, pkey=private_key, timeout=timeout)
        elif sshpassword:
            ssh.connect(pip, username=sshuser, password=sshpassword, timeout=timeout)
        else:
            raise ValueError("Either keypath or password must be provided for authentication")

        print(f"Connected to VM with IP: {pip}")
        return ssh
    except (paramiko.AuthenticationException, socket.timeout, Exception) as e:
        print(f"Error connecting to VM: {e}")
        return None

def create_snapshot_and_attach_existing_managed_disks(targetresource_group, resource_group, vm, newvm_name, snapskudisk, subscriptionid, vminf, new_disk_name_template):
### This function aiming to:
    ## Get the list of data disks attached to the VM in the VM mentioned in the variable 'vm_name' and new_vm_name ;
    ## Create snapshot of all disks found
    ## create a new disk from those snapshot;
    ## Attach those disks in the VM mentioned in the variable 'new_vm_name'
    ## 
    subscription_id = subscriptionid
    credential = DefaultAzureCredential()

    compute_client = ComputeManagementClient(credential, subscription_id)
    vminf = compute_client.virtual_machines.get(resource_group, vm)

    # Retrieve the managed disks attached to the VM
    managed_disks = vminf.storage_profile.data_disks

    # Now you can loop through the managed disks and do whatever you need
    for index, data_disk in enumerate(managed_disks):
        managed_disks_id = data_disk.managed_disk.id
        if managed_disks_id:
            # Access the managed disk details, e.g., data_disk.name, data_disk.managed_disk.id, etc.
            print(f"Managed Disk Name: {data_disk.name}")
            snapshot_name = f'snap-{vm}-datadisk-{index}'
            new_disk_name = f'{new_disk_name_template}-datadisk-{index}'

            # Create snapshot
            #print(f"Creating snap for managed Disk Name: {data_disk.name}")
            disk_creation_result = compute_client.snapshots.begin_create_or_update(
                    targetresource_group,
                    snapshot_name,
                    {
                        'location': vminf.location,
                        'creation_data': {
                            'create_option': 'Copy',
                            'source_uri': data_disk.managed_disk.id
                        }
                    }
                ).result()
            #snapshot = async_snapshot_creation.result()
            #return async_snapshot_creation  # Return the asynchronous operation

            if disk_creation_result:
                print(f"Snapshot '{snapshot_name}' creation in progress. Result: {disk_creation_result.name}")
            
            # Create new disk
            disk_creation_result = compute_client.disks.begin_create_or_update(
                targetresource_group,
                new_disk_name,
                {
                    'location': vminf.location,
                    'creation_data': {
                        'create_option': DiskCreateOption.copy,
                        'source_resource_id': disk_creation_result.id
                    },
                    'sku': {'name': snapskudisk}
                }
            ).result()
            print(f"Disk from snapshot '{disk_creation_result.name}' created successfully.")

            managed_disk = compute_client.disks.get(targetresource_group, new_disk_name)
            vminf_target = compute_client.virtual_machines.get(targetresource_group, newvm_name)

            # Get the list of data disks attached to the VM
            data_disks_target = vminf_target.storage_profile.data_disks
            # Attach the new disk to the VM
            if data_disks_target:
                used_luns = {disk.lun for disk in data_disks_target}
                new_lun = next(lun for lun in range(len(data_disks_target) + 1) if lun not in used_luns)
            else:
                new_lun = 0

            new_data_disk = DataDisk(
                lun=new_lun,
                create_option=DiskCreateOptionTypes.attach,
                managed_disk={'id': managed_disk.id}
            )
            vminf_target.storage_profile.data_disks.append(new_data_disk)

            async_update = compute_client.virtual_machines.begin_create_or_update(
                targetresource_group,
                vminf_target.name,
                vminf_target,
            )
            async_update.wait()
            print(f"Attached .")

def get_managed_disks(resource_group, subscriptionid):
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscriptionid)

    disks = compute_client.disks.list_by_resource_group(resource_group)

    return list(disks)

def create_vm_from_snap(securityType, nsg_name, attach_nic, nic_name, targetresource_group, rg_vnet, resource_group, disk, vnetnetid, subnetid, snapshot, subscriptionid, snapskudisk, newvm_name, vmsize):
### This function aiming to:
    ## create a new disk from this snapshot mentioned variable 'snapshot_name' on main file;
    ## Create new a NIC in the same VNET/Sbunet of VM mentioned in the variable 'vm_name'
    ## 
    #attach_nic = True or False
    subscription_id = subscriptionid
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Get the VM
    snapinf = compute_client.snapshots.get(resource_group, snapshot)
    # Get the OS disk ID
    snap_id = snapinf.id
   
    if snap_id:
        # Snapshot created already
        snapshot_creation_result = snapshot

        # Create disk from snapshot
        disk_creation_result = compute_client.disks.begin_create_or_update(
            targetresource_group,
            disk,
            {
                'location': snapinf.location,
                'creation_data': {
                    'create_option': DiskCreateOption.copy,
                    'source_resource_id': snap_id
                },
                'sku': {'name': snapskudisk}
            }
        ).result()
        print(f"Snapshot '{snapshot}' been used.")
        print(f"Disk from snapshot '{disk_creation_result.name}' created successfully.")

        # NIC proprieties 
        new_nic_params = {
            'location': snapinf.location,
            'ip_configurations': [{
                'name': 'ipconfig1',
                'subnet': {
                    'id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'.format(
                        subscription_id, rg_vnet, vnetnetid, subnetid)
                }
            }]
            #'network_security_group': {
            #    'id': '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/networkSecurityGroups/{}'.format(
            #        subscription_id, rg_vnet, nsg_name)
            #}
        }
        if attach_nic: 
            # Attach a NIC already created
            network_client = NetworkManagementClient(credential, subscription_id)
            new_nic = network_client.network_interfaces.begin_create_or_update(
                rg_vnet,
                nic_name,
                new_nic_params
            ).result()
            print(f"NIC '{new_nic.name}' attached successfully.")
        else:
            # Create a new NIC
            network_client = NetworkManagementClient(credential, subscription_id)
            new_nic = network_client.network_interfaces.begin_create_or_update(
                targetresource_group,
                f"nic-{newvm_name}",
                new_nic_params
            ).result()
            print(f"NIC '{new_nic.name}' created successfully.")

        # Create a new VM from the disk
        vm_creation_params = compute_client.virtual_machines.begin_create_or_update(
            targetresource_group,
            newvm_name,
            {
                'location': snapinf.location,
                'storage_profile': {
                    'os_disk': {
                        'os_type': 'Linux',
                        'create_option': DiskCreateOption.attach,
                        'managed_disk': {
                            'id': disk_creation_result.id #, 'storage_account_type': snapskudisk # Specify the appropriate storage account type
                        }
                    }
                },
                'hardware_profile': {
                    'vm_size': vmsize
                },
                'network_profile': {
                    'network_interfaces': [{
                        'id': new_nic.id
                    }]
                },
                "securityProfile": {
                    #"uefiSettings": {
                    #"secureBootEnabled": True,
                    #"vTpmEnabled": True
                    #},
                    "securityType": securityType # Trustedlaunch or Standard
                }
        }).result()
        #compute_client.virtual_machines.create_or_update(resource_group, newvm_name, vm_creation_params)
        print(f"VM '{newvm_name}' created successfully from the disk.")
    else:
        print(f"Could not find the OS disk ID for VM '{vm_name}'.")

def delete_vm(resource_group, vm, subscriptionid, vminf):
### This function aiming to:
    ## Create a snapshot of the OS disk lives in the VM mentioned in the variable 'vm_name';
    ## create a new disk from this snapshot;
    ## Create new a NIC in the same VNET/Sbunet of VM mentioned in the variable 'vm_name'
    ## 

    subscription_id = subscriptionid
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Get the VM
    vminf = compute_client.virtual_machines.get(resource_group, vm)
    # Get the OS disk ID
    os_disk_id = vminf.storage_profile.os_disk.name
   
    if os_disk_id:

        # Delete VM
        vm_delete = compute_client.virtual_machines.begin_delete(
            resource_group,
            vm)
        print(f"VM '{vm}' deleted successfully.")

         # Delete Os Disk
        vm_os_disk = compute_client.disks.begin_delete(resource_group,os_disk_id)
        print(f"disk '{os_disk_id}' deleted successfully.")

def attach_existing_managed_disks(targetresource_group, resource_group, newvm_name, subscriptionid, disk_managed_name):
### This function aiming to:
    ## Get the list of data disks attached to the VM in the VM mentioned in the variable 'vm_name' and new_vm_name ;
    ## Create snapshot of all disks found
    ## create a new disk from those snapshot;
    ## Attach those disks in the VM mentioned in the variable 'new_vm_name'
    ## 
    subscription_id = subscriptionid
    credential = DefaultAzureCredential()

    compute_client = ComputeManagementClient(credential, subscription_id)
    vminf = compute_client.virtual_machines.get(targetresource_group, newvm_name)

    managed_disks = get_managed_disks(resource_group, subscription_id)
    
    # Filter managed_disks for Unattached disks
    unattached_disks = [disk for disk in managed_disks if disk.disk_state == "Unattached" and disk.name in disk_managed_name]

    for index, disk in enumerate(unattached_disks):
        print(f"Managed Disk Name: {disk.name}")
        print(f"Disk State: {disk.disk_state}")
        print(f"Getting if condition")
        # Access the managed disk details, e.g., data_disk.name, data_disk.managed_disk.id, etc.
        new_disk_name = disk.name

        managed_disk = compute_client.disks.get(targetresource_group, new_disk_name)
        vminf_target = compute_client.virtual_machines.get(targetresource_group, newvm_name)

        # Get the list of data disks attached to the VM
        data_disks_target = vminf_target.storage_profile.data_disks
        # Attach the new disk to the VM
        if data_disks_target:
            used_luns = {disk.lun for disk in data_disks_target}
            new_lun = next(lun for lun in range(len(data_disks_target) + 1) if lun not in used_luns)
        else:
            new_lun = 0

        new_data_disk = DataDisk(
            lun=new_lun,
            create_option=DiskCreateOptionTypes.attach,
            managed_disk={'id': managed_disk.id}
        )
        vminf_target.storage_profile.data_disks.append(new_data_disk)

        async_update = compute_client.virtual_machines.begin_create_or_update(
            targetresource_group,
            vminf_target.name,
            vminf_target,
        )
        async_update.wait()
        print(f"Attached.")
    else:
        print(f"No Unattached disks found.")