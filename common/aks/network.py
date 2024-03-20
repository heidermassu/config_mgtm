from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from openpyxl import Workbook
from azure.core.exceptions import ResourceNotFoundError
from kubernetes import client, config
from azure.mgmt.containerservice import ContainerServiceClient

# Initialize Azure credentials
credentials = ''
subscription_id = ''

# Initialize AKS client
aks_client = ContainerServiceClient(credentials, subscription_id)

# Function to get AKS service ips across all namespaces
def get_all_service_ips_aks(resource_group_name, cluster_name):
    # Load kubeconfig file
    config.load_kube_config()

    # Create Kubernetes API client
    api_instance = client.CoreV1Api()

    # Dictionary to store service IPs
    all_service_ips = {}

    # Retrieve list of namespaces
    namespaces = api_instance.list_namespace().items

    # Iterate through namespaces
    for namespace in namespaces:
        namespace_name = namespace.metadata.name

        # Retrieve list of services in the namespace
        services = api_instance.list_namespaced_service(namespace=namespace_name).items

        # Iterate through services in the namespace and retrieve their IP addresses
        for service in services:
            service_name = service.metadata.name
            service_ip = service.spec.cluster_ip
            service_type = service.spec.type if service.spec.type else "Unknown"  # Default to "Unknown" if type is not provided

            # Store the service IP address and type in the dictionary
            if namespace_name not in all_service_ips:
                all_service_ips[namespace_name] = {}
            all_service_ips[namespace_name][service_name] = (service_ip, service_type)

    return all_service_ips