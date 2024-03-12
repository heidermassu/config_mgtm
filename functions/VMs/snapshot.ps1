
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope LocalMachine
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser

# Check if the Azure PowerShell module is installed
if (-not (Get-Module -Name Az.Accounts)) {
    Install-Module -Name Az.Accounts -Force -AllowClobber -Scope AllUsers
} else {
        Write-Output "Already installed Az.Accounts"
    } 

if (-not (Get-Module -Name Az.Compute)) {
    Install-Module -Name Az.Compute -Force -AllowClobber -Scope AllUsers
}else {
        Write-Output "Already installed Az.Compute"
    } 

# Define the names of the specific VMs you want to target
$targetVmNames = @("vm1", "vm2")

# Define the names of the specific Resource Group you want to save the Snaps
$rg = "rg-vm"
# Authenticate to Azure (Make sure you have the Azure PowerShell module installed)
Connect-AzAccount

# Loop through each VM name and get the VM details
foreach ($vmName in $targetVmNames) {
    $vm = Get-AzVM -Name $vmName -ErrorAction SilentlyContinue
    if ($vm) {
        # Create a snapshot configuration
        $snapshotConfig =  New-AzSnapshotConfig `
            -SourceUri $vm.StorageProfile.OsDisk.ManagedDisk.Id `
            -Location $vm.Location `
            -CreateOption Copy `
            -SkuName Standard_LRS

        # Extract resource group and VM name
        #$resourceGroupName = $vm.ResourceGroupName
        $resourceGroupName = $rg
        $resourceName = $vm.Name

        # Define snapshot name with a timestamp
        $snapshotName = "$resourceName-Snap-$(Get-Date -Format 'yyyyMMddHHmmss')"

        # Create a snapshot
        $snapshot = New-AzSnapshot -Snapshot $snapshotConfig -SnapshotName $snapshotName -ResourceGroupName $resourceGroupName

        # Output information
        Write-Output "Snapshot created for VM $vmName in Resource Group $resourceGroupName. Snapshot name: $snapshotName"
    } else {
        Write-Output "VM $vmName not found. Skipping snapshot creation."
    }
}
