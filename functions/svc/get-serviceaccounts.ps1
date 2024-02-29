Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope LocalMachine
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser

# Install and Import Azure PowerShell Module (if not already done)
if (-not (Get-Module -Name Az.Accounts)) {
    Install-Module -Name Az.Accounts -Force -AllowClobber -Scope AllUsers
} else {
        Write-Output "Already installed Az.Accounts"
    } 

# Login to Azure
Connect-AzAccount

# Retrieve the List of Service Accounts
$serviceAccounts = Get-AzADServicePrincipal

# Define the output file path
$outputFilePath = "outcome/svc.txt"

# Display and Save the Information
foreach ($account in $serviceAccounts) {
    $output = "DisplayName: $($account.DisplayName), ApplicationId: $($account.ApplicationId)"
    Write-Output $output
    Add-Content -Path $outputFilePath -Value $output
}

Write-Output "Service account information has been saved to $outputFilePath"
