from kubernetes import client, config

def get_all_service_ips():
    # Load kubeconfig file
    config.load_kube_config()

    # Create Kubernetes API client
    api_instance = client.CoreV1Api()

    # Retrieve list of namespaces
    namespaces = api_instance.list_namespace().items

    # Dictionary to store service IPs
    all_service_ips = {}

    # Iterate through namespaces
    for namespace in namespaces:
        namespace_name = namespace.metadata.name

        # Retrieve list of services in the namespace
        services = api_instance.list_namespaced_service(namespace=namespace_name).items

        # Iterate through services in the namespace and retrieve their IP addresses
        for service in services:
            service_name = service.metadata.name
            service_ip = service.spec.cluster_ip

            # Store the service IP address in the dictionary
            if namespace_name not in all_service_ips:
                all_service_ips[namespace_name] = {}
            all_service_ips[namespace_name][service_name] = service_ip

    return all_service_ips

if __name__ == "__main__":
    # Retrieve service IPs across all namespaces
    all_service_ips = get_all_service_ips()

    # Print the service IPs
    print("Service IPs:")
    for namespace, services in all_service_ips.items():
        print(f"Namespace: {namespace}")
        for service_name, service_ip in services.items():
            print(f"  {service_name}: {service_ip}")
