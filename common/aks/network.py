from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from openpyxl import Workbook
from azure.core.exceptions import ResourceNotFoundError
from kubernetes import client, config
from azure.mgmt.containerservice import ContainerServiceClient
import subprocess
import yaml

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
        try:
            # Load kubeconfig file for the current cluster
            print(f"Loading kube_config context for {cluster_name}")
            config.load_kube_config(context=cluster_name)
        except Exception as e:
            print(f"Failed to load kubeconfig for cluster {cluster_name}: {e}")
            continue
 
        # Create Kubernetes API client
        api_instance = client.CoreV1Api()
 
        # Dictionary to store service information for the current cluster
        cluster_info = {}
 
        # Retrieve list of namespaces for the current cluster
        namespaces = api_instance.list_namespace().items
 
        # Iterate through namespaces
        print(f"Gathering services for: {cluster_name}")
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
                    "External IP": external_ip,
                    # Add more fields as needed
                }
 
            # Add the namespace_services dictionary to the cluster_info dictionary
            cluster_info[namespace_name] = namespace_services
 
        # Add the cluster_info dictionary to the all_cluster_info dictionary
        all_cluster_info[cluster_name] = cluster_info
 
    return all_cluster_info


def parse_ingress_kubectl(output):
    ingresses = []
    lines = output.strip().split('\n')[1:]  # Split the output into lines, skip header
    for line in lines:
        fields = line.split()
        ingress = {
            "NAMESPACE": fields[0],
            "NAME": fields[1],
            "CLASS": fields[2],
            "HOSTS": fields[3].split(','),
            "ADDRESS": fields[4],
            "PORTS": fields[5],
            "AGE": fields[6]
        }
        ingresses.append(ingress)
    return ingresses
 
def list_ingress_kubectl(cluster_names):
    all_ingresses = []
    for cluster_name in cluster_names:
        try:
            # Load kubeconfig file for the current cluster
            print(f"Loading kube_config context for {cluster_name}")
            config.load_kube_config(context=cluster_name)

            # Run kubectl command to set the right current context
            current_context = subprocess.run(["kubectl", "config", "use-context", cluster_name],
                                     capture_output=True, text=True, check=True)
            print(f"settling context: {current_context.stdout}")# debbugging

        except Exception as e:
            print(f"Failed to load kubeconfig for cluster {cluster_name}: {e}")
            break

        # Create Kubernetes API client
        api_instance = client.CoreV1Api()

        try:

            # Run kubectl command to get current context
            current_context = subprocess.run(["kubectl", "config", "current-context"],
                                     capture_output=True, text=True, check=True)
            print(f"current context: {current_context.stdout}")# debbugging

            # Run kubectl command to get Ingress resources
            result = subprocess.run(["kubectl", "get", "ingress", "--all-namespaces", "-o", "wide"],
                                     capture_output=True, text=True, check=True)
            #print("Ingress configurations:") # debbugging
            #print(result.stdout)# debbugging
            
            # Parse the output and append to the list of ingresses
            ingresses = parse_ingress_kubectl(result.stdout)
            all_ingresses.extend(ingresses)
        except subprocess.CalledProcessError as e:
            print("Error executing kubectl:", e)
    return all_ingresses

##def list_ingress_kubectl(cluster_names):
##    for cluster_name in cluster_names:
##        try:
##            # Load kubeconfig file for the current cluster
##            print(f"Loading kube_config context for {cluster_name}")
##            config.load_kube_config(context=cluster_name)
##        except Exception as e:
##            print(f"Failed to load kubeconfig for cluster {cluster_name}: {e}")
##            continue
##
##        try:         # Run kubectl command to get Ingress resources        
##            result = subprocess.run(["kubectl", "get", "ingress", "--all-namespaces", "-o", "wide"],
##            capture_output=True, text=True, check=True)        
##            print("Ingress configurations:")        
##            print(result.stdout)     
##        except subprocess.CalledProcessError as e:         
##            print("Error executing kubectl:", e) 
##        return result.stdout