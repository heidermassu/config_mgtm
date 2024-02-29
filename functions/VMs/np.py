import re
import csv
import sys
 
def read_servers_from_file(targetVmNames):
    try:
        with open(targetVmNames, 'r') as file:
            # Read lines, strip whitespace, and filter out empty lines
            servers = [line.strip() for line in file if line.strip()]
        return servers
    except FileNotFoundError:
        print(f"Error: File '{targetVmNames}' not found.")
        sys.exit(1)
 
def group_servers_by_pattern(servers, patterns):
    grouped_servers = []
    for server in servers:
        application = ""
        environment = ""
        for pattern, regex in patterns.items():
            if re.search(regex, server):
                application = pattern
                break
        if re.search(r"-p1|-p2|prod|gumbo", server):
            environment = "Production"
        elif re.search(r"-t1|-t2|test", server):
            environment = "Test"
        elif re.search(r"-s|staging|stg|1s|2s", server):
            environment = "Staging"
        grouped_servers.append([server, application, environment])
    return grouped_servers
 
def save_to_csv(grouped_servers, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header
        header = ['Server', 'Application', 'Environment']
        csv_writer.writerow(header)
        # Write data
        csv_writer.writerows(grouped_servers)
 
if len(sys.argv) < 2:
    print("Usage: python script.py <input_file>")
    sys.exit(1)
 
input_file = sys.argv[1]
 
# Read servers from the file using the function
servers = read_servers_from_file(input_file)
 
# Define patterns for different applications
application_patterns = {
    "Aurora": r"aurora",
    "Amethyst": r"amethy",
    "bamboo": r"bamboo",
    "bitb": r"bitb",
    "ClamAV": r"clamav",
    "CORA": r"cora",
    "Clone": r"clone",
    "DNSForward": r"azdev",
    "Dora": r"dora",
    "Elasticsearch": r"elsearch",
    "Impala": r"imp",
    "Orca": r"orca",
    "Prometheus_Grafana": r"(prometheus|grafana)",
    "Portal": r"(portal|ivdportal)",
    "Picasso": r"picasso",
    "pipeline": r"p-",
    "selenium": r"selenium",
    "sybil": r"sybil",
    "Sequencing_YUM": r"(seqam|yum)",
    "JumpingServer": r"ansible",
   
}
 
# Group servers based on defined patterns and environments
grouped_servers = group_servers_by_pattern(servers, application_patterns)
 
# Save grouped servers to CSV
csv_filename = 'outcome/patterners_name.csv'
save_to_csv(grouped_servers, csv_filename)
 
print(f"Grouped servers saved to {csv_filename}.")