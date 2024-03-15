# SRE Team Scripts

## Table of Contents
- [Goal](#Goal)
- [Branch Strategy](#Branch-Strategy)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [How to submit new script?](#How-to-submit-new-script)

 
## Goal
 
This project serves as the central repository for all scripts and snippets utilized by the SRE Team in handling tickets or included in Playbooks/Runbooks.
 
## Contributing
 
For Virtasant members, to contribute to this repository, follow these steps:
 
1. Clone the repository.
2. Create a new branch: `git checkout -b <descriptive_branch_name>`.
3. Make your changes and commit them: `git commit -m 'Add/Modify/Delete ....'`.
4. Push to the branch: `git push origin <descriptive_branch_name>`.
5. Submit a pull request.

## Branch Strategy
GitHub Flow:
Description: A simplified workflow that relies on a single main branch (often named main or master). Features are developed in branches and merged directly into the main branch via pull requests. Continuous deployment is often part of this workflow.
- Pros:
    - Simplicity and ease of use.
    - Well-suited for continuous delivery.
- Cons:
    - May lack a clear staging area for releases.

## Getting Started
 
### Prerequisites
 
List any software, dependencies, or tools that will be necessary to have installed before we can use the scripts.
- Makefile commands
 
### Installation
 
Provide step-by-step instructions on how to install and set up your project. Include any configuration steps if necessary.

## How to submit new script?
The idea is have all scripts executed through Makefile

## Main Variables
For each Main function there are a bunch of variables have to be filled with the inforamtion related to either resources are created or going to be created. All Main Functions has comments in the variables given inforamtion what is used for.
Nevertheless, here goes all Variables and their propose.
OBs. Those ones are all variables but you will notice the main function may not have all variables but only the necessary variables.

### Varibales:
Replace the following variables with your own values
- resource_group_name = '' # Replace with the RG regarding the source VM
- target_resource_group = '' # Replace with the RG regarding the where you want to create the new VM.Could be same RG the old but necessary delete the old one.
- vm_name = '' # Replace with the RG regarding the where you want to create the new VM
- snapshot_name = '' # Snapshot name going to be created
- new_disk_name = '' # Managed Disk name name going to be created
- new_vm_name = '' # New VM name going to be created
- vm_size = 'Standard_DS1_v2'  # Replace with the desired VM size
- subscription_id = '' # Replace with the subscription Id where is based the VM
- key_path = r'' # in case you are using pem to aut in linux here is the local where is your pem
- ssh_user = '' # This one is used for both authetication (pem and user/pass)
- ssh_password = '' # used only for user/pass authentication
- disk_name = '' # OS disk name going to be created
- snap_skudisk= '' # You have only 2 choise ## Premium_LRS,Standard_LRS
- nic_name = ''  # Nic name going to be created and attached as temp in the old VM.#Should be filled only if 'attach_nic' is 'True' otherwise will not have
- ip_configuration_name = "ipconfig1" # name of the IP configuration under NIC
- private_ip_address_allocation = "Dynamic" # type of configuration of the IP could be Dynamic or Standard
- subnet_id = "default" # subnet ID where is the NIC that want to be detached and also where going to be created new nic temp. Obs both have to be same VNET
- vnetnet_id = "vm01-vnet" # VNET ID where is the NIC that want to be detached and also where going to be created new nic temp. Obs both have to be same VNET
- rg_vnet = ''# RG where is the VNET
- rg_nic = '' # RG where is the NIC
- vm = 'heider-vm01' # vm name that have to be restored
- disk ='disk-from-snap4' #name of the os disk going to be created for the new VM
- disk_managed_name = ['heider-vm01_DataDisk_2', 'heiderDataDisk_1'] # In case there are managed disks attached fill with the names ['disk'', 'disk2']
- snapskudisk = 'Premium_LRS' # You have only 2 choise ## Premium_LRS,Standard_LRS
- newvm_name = 'heider-vm01' # Name of the new vm going to be created. Could be same name but the flag 'del_vm' have to be 'True' otherwise will get error due to have vm with same name 
- vmsize = 'Standard_D2s_v3' # Replace with the desired VM size
- securityType = 'Trustedlaunch' # Trustedlaunch or Standard
- del_vm = True #True or False.  True going to delete vm (used when you want create with same name same RG.) False going to leave the old VM as deallocated
- attach_nic = True #True or False
- nsg_name = 'heider-vm01-nsg' #This is the NSG going to be either attached in the new vm or created if do not have
- nic_name = 'heider-vm01647' #Should be filled only if 'attach_nic' is 'True' otherwise will not have impact. this is the NIC going to be attached in the new vm


## Main Functions

### Resizing VM
- Resizing VM 'vm-main-resizing.py'
  - Automatic Steps:
    - 1º ssh into server
    - 2º Stop the services kudu-server, impalad and hadoop-hdfs-datanode'
    - 3º Stop System operation
    - 4º Deallocate VM
    - 5º take Snapshot of OS disk and managed disk attached
    - 6º Create a new disks from those Snapshots 
    - 7º Create a new VM from the OS disk created and choose the new VM size 
    - 7.1º Attach the new managed disk created
    - 8º Make Private IP address static on NIC, Detach NIC from the old VM and attach it in the new VM
    - 9º start the new VM

### Deallocating VM
- Resizing VM 'deallocating-vm-main.py'
  - Going to deallocate VM settled in the variables

### Snapshoting VM os Disk
- Resizing VM 'snapshot-vm-os-main.py'
  - Going to create a snapshot of the VM mentioned

### Restoring VM from snapshot
- Resizing VM 'restore-vm-from-snap-main.py'
  - Going to restore a new VM based on Snapshot name provided
    - steps:
      - 1º Going to deallocate old VM settled in the variables
      - 2º Delete the old VM were deallocated (only if the variable 'del_vm = True')
      - 3º Create a New vm from snapshot name provided in the variable 'snapshot'. You must have a snapshot created already that ensure you can restore that specifi point of time!! Otherwise will not posible restore
        - 3.1 - Create disk from snapshot
        - 3.2 - Create a new NIC or Attach NIC already created
        - 3.3 - Create a new VM from the disk
      - 4º Attach managed disk providen through variable 'disk_managed_name' 


## Functions
### Module common.vm.vm
- create_snapshot_os_disk
  - This function aiming to create a snapshot of the OS disk lives in the VM mentioned in the variable vm_name';

- create_snap_and_vm
  - This function aiming to create a snapshot of the OS disk lives in the VM mentioned in the variable 'vm_name'; create a new disk from this snapshot; Create new a NIC in the same VNET/Sbunet of VM mentioned in the variable 'vm_name'

- deallocating_vm
  - This function aiming to deallocate the VM mentioned in the variable 'vm_name';

- get_vm_status
  - This function aiming to get the VM status of the VM mentioned in the variable 'vm_name';

- start_vm_created
  - This function aiming to start the VM is mentioned in the variable new_vm_name

- execute_ssh_commands_stop
  - SSH into the VM and execute commands to stop services

- execute_ssh_commands_start
  - SSH into the VM and execute commands to start services

- ssh_into_vm
  - SSH into the VM 

- create_snapshot_and_attach_existing_managed_disks
  - This function aiming to get the list of data disks attached to the VM in the VM mentioned in the variable 'vm_name' and new_vm_name ; Create snapshot of all disks found; create a new disk from those snapshot; Attach those disks in the VM mentioned in the variable 'new_vm_name'

- delete_vm
  - Delete a VM and Os Disk related to it
  
- create_vm_from_snap
  - create a new disk from this snapshot mentioned variable 'snapshot_name' on main file (restore-vm-from-snap-main.py);
  - Create new either a NIC in the same VNET/Sbunet of VM mentioned in the variable 'vm_name' or attach NIC already created

- attach_existing_managed_disks
  -  Get the list of managed disks attached filtering for Unattached disks and also by name disk mentioned in the main variable 'disk_managed_name'and then add those disks as managed disks

- get_managed_disks
  - Get the full list of disks

### Module common.network.network
- create_nic
- nic_attach