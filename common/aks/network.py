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
cluster_name = ''

# Initialize AKS client
aks_client = ''

# Function to get AKS service IPs across all namespaces
def get_all_service_ips_aks(resource_group_name, cluster_names):
    # Dictionary to store service information for all clusters
    all_cluster_info = {}

    for cluster_name in cluster_names:
        # Load kubeconfig file for the current cluster
        config.load_kube_config(context=cluster_name)

        # Create Kubernetes API client
        api_instance = client.CoreV1Api()

        # Dictionary to store service information for the current cluster
        cluster_info = {}
        print(f"Cluster Name: {cluster_name}")  # debugging

        # Retrieve list of namespaces for the current cluster
        namespaces = api_instance.list_namespace().items
        #print(f"Namespaces for {cluster_name}: {namespaces}")  # debugging

        # Iterate through namespaces
        for namespace in namespaces:
            namespace_name = namespace.metadata.name

            # Retrieve list of services in the namespace for the current cluster
            services = api_instance.list_namespaced_service(namespace=namespace_name).items

            # Dictionary to store service information for the current namespace
            namespace_services = {}

            # Iterate through services in the namespace and retrieve their details
            for service in services:
                service_name = service.metadata.name
                service_ip = service.spec.cluster_ip
                service_type = service.spec.type if service.spec.type else "Unknown"

                # Retrieve external IP if available
                external_ip = None
                load_balancer_ingress = service.status.load_balancer.ingress
                if load_balancer_ingress:
                    external_ip = load_balancer_ingress[0].ip

                # Add service information to the namespace_services dictionary
                namespace_services[service_name] = {
                    "IP": service_ip,
                    "Type": service_type,
                    "External IP": external_ip
                    # Add more fields as needed
                }

            # Add the namespace_services dictionary to the cluster_info dictionary
            cluster_info[namespace_name] = namespace_services

        # Add the cluster_info dictionary to the all_cluster_info dictionary
        all_cluster_info[cluster_name] = cluster_info

    return all_cluster_info
