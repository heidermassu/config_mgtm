# Prerequisite #
## Necessary to install make commands in your machine#

##VARIABLES
targetVmNames ?= common-steps/txt/test.txt
subscription ?= ""


.PHONY: vm

## Used to create a csv which going to have these tags columns VMName; Owner; CostCenter; BusinessUnit and Environment
tags:
	sh ./functions/VMs/get-tags.sh "$(subst /,\,$(targetVmNames))"

## Used to create a csv which going to have 3 columns server (name in the list provided); application will be given by name pattern the server has same for the enviroment.
name-patterns:
	py ./functions/VMs/np.py "$(subst /,\,$(targetVmNames))"

test:
	py ./functions/testing/vms.py "$(subst /,\,$(targetVmNames))"

svc-details:
	powershell -file ./functions/svc/get-serviceaccounts.ps1

vm: name-patterns tags
svc: svc-details
all: name-patterns vm-tags svc-details