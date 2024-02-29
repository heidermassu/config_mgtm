import sys


from common import initialize_variables, create_vm_from_snap, start_vm_created, deallocating_vm, get_vm_status, execute_ssh_commands_stop, execute_ssh_commands_start, ssh_into_vm, create_snapshot_and_attach_existing_managed_disks
from common import initialize_variables, create_nic, nic_attach

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption, DiskCreateOptionTypes, DataDisk
import time

# Replace the following variables with your own values
resource_group_name = 'manual' # Replace with the RG regarding the source VM
target_resource_group = 'aut' # Replace with the RG regarding the where you want to create the new VM
vm_name = 'vm1' # Replace with the RG regarding the where you want to create the new VM
location = 'WestUS' # Have to be same location of source VM
snapshot_name = 'snap-vm1' # Snapshot name going to be created
new_disk_name = 'vm1-new-test' # Managed Disk name name going to be created
new_vm_name = 'vm1' # New VM name going to be created
vm_size = 'Standard_DS1_v2'  # Replace with the desired VM size
subscription_id = '' # Replace with the subscription Id where is based the VM
key_path = r'' # in case you are using pem to aut in linux here is the local where is your pem
ssh_user = 'heider' # This one is used for both authetication (pem and user/pass)
ssh_password = 'Change@1234567' # used only for user/pass authentication
disk_name = 'vm1_disk1_338c7ee9869344e2a018786f43523253' # OS disk name going to be created
snap_skudisk= 'Premium_LRS' # You have only 2 choise ## Premium_LRS,Standard_LRS
nic_name = 'nic-vm1-temp'  # Nic name going to be created and attached as temp in the old VM
# Define NIC Parameters
ip_configuration_name = "ipconfig1"
private_ip_address_allocation = "Dynamic"
subnet_id = "default" # subnet ID where is the NIC that want to be detached and also where going to be created new nic temp. Obs both have to be same VNET
vnetnet_id = "vm1-vnet" # VNET ID where is the NIC that want to be detached and also where going to be created new nic temp. Obs both have to be same VNET
rg_vnet = 'manual'# RG where is the VNET
rg_nic = 'manual' # RG where is the NIC

# Connect to Azure and get VM information
credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)

# Get VM information
vm_inf = compute_client.virtual_machines.get(resource_group_name, vm_name)


## Get public and private IP addresses of the VM
network_interface_id = vm_inf.network_profile.network_interfaces[0].id
network_interface = network_client.network_interfaces.get(rg_nic, network_interface_id.split('/')[-1])
private_ip_address = network_interface.ip_configurations[0].private_ip_address
print(f"Private IP address: {private_ip_address}")

# Retrieve public IP address if it exists
if network_interface.ip_configurations[0].public_ip_address:
    public_ip_id = network_interface.ip_configurations[0].public_ip_address.id
    public_ip_address = network_client.public_ip_addresses.get(rg_nic, public_ip_id.split('/')[-1]).ip_address
    print(f"Public IP address: {public_ip_address}")
else:
    public_ip_address = None
    print("No public IP address associated with the VM.")

# Execute commands on the VM
stoping_commands = [
    'sudo hostname',
    'sudo systemctl stop impalad',
    'sudo systemctl stop kudu-tserver',
    'sudo systemctl stop hadoop-hdfs-datanode',
    'sudo systemctl poweroff'
]

starting_commands = [
    'sudo hostname'
]

# Check the VM status
vm_status = get_vm_status(compute_client, resource_group_name, vm_name)

# Log the VM status
print(f"VM '{vm_name}' status: {vm_status}")

# Check if the VM is running before attempting SSH
if vm_status != 'VM running':

    sshconnection = None

    # Used to initiate the variables going to be used for the others python files 
    initialize_variables(resource_group_name, resource_group_name, vm_name, disk_name, stoping_commands, snapshot_name, vm_inf, subscription_id, public_ip_address, ssh_user, key_path, sshconnection, snap_skudisk, new_disk_name, new_vm_name, vm_size, starting_commands, nic_name, location, vnetnet_id, subnet_id, ip_configuration_name, private_ip_address_allocation)
    
    print("VM is not in a running state. Skipping SSH and proceeding with other steps.")

# Perform actions taking snapshot, creating disk, creating vm from this disk
    create_vm_from_snap(target_resource_group, rg_vnet, resource_group_name, vm_name, disk_name, vnetnet_id, subnet_id, snapshot_name, subscription_id, vm_inf, snap_skudisk, new_disk_name, new_vm_name, vm_size)

# Perform actions deallocating VM
    deallocating_vm(target_resource_group, new_vm_name, subscription_id)

# Perform actions creating new nic, aataching new nic to old vm and attaching prod nic to new vm
    nic_attach (target_resource_group, rg_vnet, resource_group_name, vm_name, new_vm_name, subscription_id, nic_name, location, vnetnet_id, subnet_id, ip_configuration_name, private_ip_address_allocation)

# Perform actions creating new snap
    create_snapshot_and_attach_existing_managed_disks(target_resource_group, resource_group_name, vm_name, new_vm_name, snap_skudisk, subscription_id, vm_inf, new_disk_name)

# Perform actions atarting the new VM new snap
    start_vm_created(target_resource_group, subscription_id, new_vm_name)

## TO FIX: After start new VM is not connecting into the new one due to the key have to be renew
    
    # Attempt to SSH into the private IP address
    #if private_ip_address:
    #    print(f"Attempting to connect to the private IP address: {private_ip_address}")
    #    sshconnection = ssh_into_vm(private_ip_address, ssh_user, key_path, ssh_password)
    ## If private IP connection fails or private IP is not available, attempt to connect to the public IP
    #if not sshconnection and public_ip_address:
    #    print(f"Attempting to connect to the public IP address: {public_ip_address}")
    #    sshconnection = ssh_into_vm(private_ip_address, ssh_user, key_path, ssh_password)
#
    #if not sshconnection:
    #    print("SSH connection failed to both private and public IP addresses. Exiting.")
    #    exit()
    #else:
    #    print(f"SSH connection successful. Using IP: {private_ip_address or public_ip_address}")

    # Introduce a delay of 4 minute
    #print("Waiting for 1 minute before executing SSH commands...")
    #time.sleep(140)

    #execute_ssh_commands_start(sshconnection, starting_commands)


else:

    # Attempt to SSH into the private IP address
    sshconnection = None
    if private_ip_address:
        print(f"Attempting to connect to the private IP address: {private_ip_address}")
        sshconnection = ssh_into_vm(private_ip_address, ssh_user, key_path, ssh_password)
    # If private IP connection fails or private IP is not available, attempt to connect to the public IP
    if not sshconnection and public_ip_address:
        print(f"Attempting to connect to the public IP address: {public_ip_address}")
        sshconnection = ssh_into_vm(public_ip_address, ssh_user, key_path, ssh_password)

    if not sshconnection:
        print("SSH connection failed to both private and public IP addresses. Exiting.")
        exit()
    else:
        print(f"SSH connection successful. Using IP: {private_ip_address or public_ip_address}")

    # Used to initiate the variables going to be used for the others python files 
    initialize_variables(resource_group_name, resource_group_name, vm_name, disk_name, stoping_commands, snapshot_name, vm_inf, subscription_id, public_ip_address, ssh_user, key_path, sshconnection, snap_skudisk, new_disk_name, new_vm_name, vm_size, starting_commands, nic_name, location, vnetnet_id, subnet_id, ip_configuration_name, private_ip_address_allocation)

    # executing commands into the VM wrote in "stoping_commands"
    execute_ssh_commands_stop(sshconnection, stoping_commands)

    # Deallocate VM
    deallocating_vm(resource_group_name, vm_name, subscription_id)

# Perform actions taking snapshot, creating disk, creating vm from this disk
    create_vm_from_snap(target_resource_group, rg_vnet, resource_group_name, vm_name, disk_name, vnetnet_id, subnet_id, snapshot_name, subscription_id, vm_inf, snap_skudisk, new_disk_name, new_vm_name, vm_size)

# Perform actions deallocating VM
    deallocating_vm(target_resource_group, new_vm_name, subscription_id)

# Perform actions creating new nic, aataching new nic to old vm and attaching prod nic to new vm
    nic_attach (target_resource_group, rg_vnet, resource_group_name, vm_name, new_vm_name, subscription_id, nic_name, location, vnetnet_id, subnet_id, ip_configuration_name, private_ip_address_allocation)

# Perform actions creating new snap
    create_snapshot_and_attach_existing_managed_disks(target_resource_group, resource_group_name, vm_name, new_vm_name, snap_skudisk, subscription_id, vm_inf, new_disk_name)

# Perform actions atarting the new VM new snap
    start_vm_created(target_resource_group, subscription_id, new_vm_name)

    # Introduce a delay of 4 minute
    #print("Waiting for 1 minute before executing SSH commands...")
    #time.sleep(140)

## TO FIX: After start new VM is not connecting into the new one due to the key have to be renew
    #execute_ssh_commands_start(sshconnection, starting_commands)