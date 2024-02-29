# going to grab information provided by variable targetVmNames in the Makefile
#targetVmNames=$(cat $(targetVmNames) | tr -d '\r' | tr '\n' ' ')
targetVmNames=$(cat "$1" | tr -d '\r' | tr '\n' ' ')
 
# Create the Azure CLI query using the filter values
query="[?tags.CostCenter && contains(\`[${targetVmNames[*]}]\`, name)].{VMName: name, Owner: tags.Owner, CostCenter: tags.CostCenter, BusinessUnit: tags.BusinessUnit, Environment: tags.Environment, OperationTeams: tags.OperationTeams }"
 
# Run the Azure CLI command with the query and save the output to a txt.
az vm list --query "$query" --output tsv > outcome/list-tags.txt