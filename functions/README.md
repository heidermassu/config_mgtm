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

## Main Functions

### Resizing VM
- Resizing VM 'VMs\vm-main-resizing.py'
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

## Functions
### Module common.vm.vm
- create_snapshot_os_disk
- create_vm_from_snap
- deallocating_vm
- get_vm_status
- start_vm_created
- execute_ssh_commands_stop
- execute_ssh_commands_start
- ssh_into_vm
- create_snapshot_and_attach_existing_managed_disks

### Module common.network.network
- create_nic
- nic_attach