from common.vm.vm import  deallocating_vm


from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption, DiskCreateOptionTypes, DataDisk
import time

resource_group = 'aut'
vm = 'vm01'
subscriptionid = ''

# Going to deallocate VM settled in the variables
deallocating_vm(resource_group, vm, subscriptionid)