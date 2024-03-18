import csv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

def main():
    subscription_id = 'a6cc1a53-c242-42f9-aa16-15a377d21069'
    resource_client = ResourceManagementClient(DefaultAzureCredential(), subscription_id)

    with open('azure_resources_info.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Resource Type', 'Resource Name', 'Resource Group', 'Location'])

        for resource in resource_client.resources.list():
            resource_type = resource.type.split('/')[-1]
            resource_name = resource.name
            resource_group = resource.id.split('/')[4]
            location = resource.location

            writer.writerow([resource_type, resource_name, resource_group, location])

    print("Resource information saved to azure_resources_info.csv")

if __name__ == "__main__":
    main()
