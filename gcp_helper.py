"""
Google Cloud Platform (GCP) specific helper functions and code generators
"""

from typing import Dict, List, Any
import json


class GCPHelper:
    """GCP-specific helper for infrastructure and code assistance"""
    
    def __init__(self):
        self.services = {
            'compute': ['Compute Engine', 'Container Engine', 'App Engine', 'Cloud Functions', 'Cloud Run'],
            'storage': ['Cloud Storage', 'Persistent Disk', 'Filestore', 'Cloud SQL'],
            'database': ['Cloud SQL', 'Firestore', 'Bigtable', 'Spanner', 'Memorystore'],
            'networking': ['VPC', 'Cloud Load Balancing', 'Cloud CDN', 'Cloud DNS', 'Cloud NAT'],
            'security': ['Identity and Access Management', 'Cloud KMS', 'Security Command Center', 'Certificate Authority'],
            'monitoring': ['Cloud Monitoring', 'Cloud Logging', 'Cloud Trace', 'Cloud Profiler']
        }
    
    def generate_terraform_compute(self, config: Dict[str, Any]) -> str:
        """Generate Terraform configuration for GCP Compute Engine"""
        template = f'''
# Configure the Google Cloud Provider
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = "{config.get('project_id', 'your-project-id')}"
  region  = "{config.get('region', 'us-central1')}"
  zone    = "{config.get('zone', 'us-central1-a')}"
}

# VPC Network
resource "google_compute_network" "{config.get('name', 'default')}_vpc" {
  name                    = "{config.get('name', 'default')}-vpc"
  auto_create_subnetworks = false
  mtu                     = 1460
}

# Subnet
resource "google_compute_subnetwork" "{config.get('name', 'default')}_subnet" {
  name          = "{config.get('name', 'default')}-subnet"
  ip_cidr_range = "{config.get('subnet_cidr', '10.0.1.0/24')}"
  region        = "{config.get('region', 'us-central1')}"
  network       = google_compute_network.{config.get('name', 'default')}_vpc.id
}

# Firewall rule to allow SSH
resource "google_compute_firewall" "{config.get('name', 'default')}_ssh" {
  name    = "{config.get('name', 'default')}-allow-ssh"
  network = google_compute_network.{config.get('name', 'default')}_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["{config.get('ssh_source', '0.0.0.0/0')}"]
  target_tags   = ["ssh-server"]
}

# Firewall rule to allow HTTP
resource "google_compute_firewall" "{config.get('name', 'default')}_http" {
  name    = "{config.get('name', 'default')}-allow-http"
  network = google_compute_network.{config.get('name', 'default')}_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
}

# Compute Engine instance
resource "google_compute_instance" "{config.get('name', 'default')}" {
  name         = "{config.get('instance_name', config.get('name', 'default') + '-instance')}"
  machine_type = "{config.get('machine_type', 'e2-micro')}"
  zone         = "{config.get('zone', 'us-central1-a')}"

  tags = ["{config.get('tags', ['ssh-server', 'web-server'])}"[0], "{config.get('tags', ['ssh-server', 'web-server'])}"[1]]

  boot_disk {
    initialize_params {
      image = "{config.get('image', 'debian-cloud/debian-11')}"
      size  = {config.get('disk_size', 20)}
      type  = "{config.get('disk_type', 'pd-standard')}"
    }
  }

  network_interface {
    network    = google_compute_network.{config.get('name', 'default')}_vpc.id
    subnetwork = google_compute_subnetwork.{config.get('name', 'default')}_subnet.id
    
    access_config {
      # Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "{config.get('ssh_user', 'admin')}:{config.get('ssh_public_key', 'your-ssh-public-key-here')}"
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y nginx
    {config.get('startup_script', '# Add your startup commands here')}
  EOF

  labels = {
    environment = "{config.get('environment', 'production')}"
    project     = "{config.get('project', 'default')}"
  }

  service_account {
    email  = "{config.get('service_account', 'default')}"
    scopes = ["cloud-platform"]
  }
}

# Static IP (optional)
resource "google_compute_address" "{config.get('name', 'default')}_static_ip" {
  name   = "{config.get('name', 'default')}-static-ip"
  region = "{config.get('region', 'us-central1')}"
}

# Output values
output "instance_ip" {
  description = "The public IP address of the instance"
  value       = google_compute_instance.{config.get('name', 'default')}.network_interface[0].access_config[0].nat_ip
}

output "instance_name" {
  description = "The name of the instance"
  value       = google_compute_instance.{config.get('name', 'default')}.name
}
        '''
        return template.strip()
    
    def generate_deployment_manager_template(self, config: Dict[str, Any]) -> str:
        """Generate Google Cloud Deployment Manager template"""
        template = {
            "imports": [
                {"path": "vm-template.jinja"}
            ],
            "resources": [
                {
                    "name": f"{config.get('name', 'default')}-deployment",
                    "type": "vm-template.jinja",
                    "properties": {
                        "zone": config.get('zone', 'us-central1-a'),
                        "machineType": config.get('machine_type', 'e2-micro'),
                        "network": config.get('network', 'default'),
                        "subnet": config.get('subnet', 'default'),
                        "sourceImage": config.get('image', 'projects/debian-cloud/global/images/family/debian-11'),
                        "diskSizeGb": config.get('disk_size', 20),
                        "tags": {
                            "items": config.get('tags', ['http-server', 'https-server'])
                        },
                        "metadata": {
                            "items": [
                                {
                                    "key": "startup-script",
                                    "value": config.get('startup_script', '''#!/bin/bash
apt-get update
apt-get install -y apache2
systemctl start apache2
systemctl enable apache2''')
                                }
                            ]
                        }
                    }
                }
            ],
            "outputs": [
                {
                    "name": "instanceName",
                    "value": f"$(ref.{config.get('name', 'default')}-deployment.name)"
                },
                {
                    "name": "instanceIP",
                    "value": f"$(ref.{config.get('name', 'default')}-deployment.networkInterfaces[0].accessConfigs[0].natIP)"
                }
            ]
        }
        
        return json.dumps(template, indent=2)
    
    def generate_cloud_function(self, config: Dict[str, Any]) -> str:
        """Generate Google Cloud Function code"""
        runtime = config.get('runtime', 'python39')
        
        if runtime.startswith('python'):
            return f'''
import functions_framework
from google.cloud import logging
import json
from typing import Dict, Any

# Initialize logging client
logging_client = logging.Client()
logging_client.setup_logging()

@functions_framework.http
def {config.get('function_name', 'hello_world')}(request):
    """
    HTTP Cloud Function: {config.get('description', 'Generated Cloud Function')}
    Args:
        request (flask.Request): The request object
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using make_response
    """
    
    try:
        # Handle preflight CORS request
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }
            return ('', 204, headers)
        
        # Set CORS headers for main request
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
        
        # Get request data
        request_json = request.get_json(silent=True)
        request_args = request.args
        
        if request_json:
            data = request_json
        elif request_args:
            data = dict(request_args)
        else:
            data = {}
        
        print(f'Request data: {json.dumps(data)}')
        
        # Your business logic here
        response_data = {
            'message': 'Function executed successfully',
            'input': data,
            'status': 'success'
        }
        
        return (json.dumps(response_data), 200, headers)
        
    except Exception as e:
        print(f'Error: {str(e)}')
        
        error_response = {
            'error': str(e),
            'status': 'error'
        }
        
        return (json.dumps(error_response), 500, {'Content-Type': 'application/json'})

# requirements.txt content:
# functions-framework==3.*
# google-cloud-logging==3.*
            '''
        
        elif runtime.startswith('nodejs'):
            return f'''
const functions = require('@google-cloud/functions-framework');
const {Logging} = require('@google-cloud/logging');

// Initialize logging
const logging = new Logging();
const log = logging.log('cloud-function-log');

functions.http('{config.get('function_name', 'helloWorld')}', (req, res) => {
    try {
        // Handle CORS
        res.set('Access-Control-Allow-Origin', '*');
        
        if (req.method === 'OPTIONS') {
            res.set('Access-Control-Allow-Methods', 'GET, POST');
            res.set('Access-Control-Allow-Headers', 'Content-Type');
            res.set('Access-Control-Max-Age', '3600');
            res.status(204).send('');
            return;
        }
        
        // Get request data
        const data = req.body || req.query || {};
        
        console.log('Request data:', JSON.stringify(data));
        
        // Your business logic here
        const responseData = {
            message: 'Function executed successfully',
            input: data,
            status: 'success'
        };
        
        res.status(200).json(responseData);
        
    } catch (error) {
        console.error('Error:', error);
        
        res.status(500).json({
            error: error.message,
            status: 'error'
        });
    }
});

// package.json content:
// {
//   "name": "{config.get('function_name', 'hello-world')}",
//   "version": "1.0.0",
//   "main": "index.js",
//   "dependencies": {
//     "@google-cloud/functions-framework": "^3.0.0",
//     "@google-cloud/logging": "^10.0.0"
//   }
// }
            '''
    
    def generate_gcp_sdk_example(self, service: str, operation: str) -> str:
        """Generate GCP SDK code examples"""
        examples = {
            'compute': {
                'list_instances': '''
from google.cloud import compute_v1

def list_all_instances(project_id: str):
    """
    List all instances in the given project in all zones.
    """
    instance_client = compute_v1.InstancesClient()
    zones_client = compute_v1.ZonesClient()
    
    # Get all zones
    zones = zones_client.list(project=project_id)
    
    for zone in zones:
        print(f"Instances in zone: {zone.name}")
        
        instances = instance_client.list(project=project_id, zone=zone.name)
        
        for instance in instances:
            print(f"  Name: {instance.name}")
            print(f"  Machine Type: {instance.machine_type}")
            print(f"  Status: {instance.status}")
            print("  ---")

# Usage
project_id = "your-project-id"
list_all_instances(project_id)
                ''',
                'create_instance': '''
from google.cloud import compute_v1
import time

def create_instance(project_id: str, zone: str, instance_name: str):
    """
    Create a new instance in the given project and zone.
    """
    instance_client = compute_v1.InstancesClient()
    
    # Configure the machine
    config = compute_v1.Instance()
    config.name = instance_name
    config.machine_type = f"zones/{zone}/machineTypes/e2-micro"
    
    # Configure the boot disk
    boot_disk = compute_v1.AttachedDisk()
    boot_disk.auto_delete = True
    boot_disk.boot = True
    boot_disk.type_ = compute_v1.AttachedDisk.Type.PERSISTENT
    
    initialize_params = compute_v1.AttachedDiskInitializeParams()
    initialize_params.source_image = "projects/debian-cloud/global/images/family/debian-11"
    initialize_params.disk_size_gb = 20
    boot_disk.initialize_params = initialize_params
    
    config.disks = [boot_disk]
    
    # Configure the network interface
    network_interface = compute_v1.NetworkInterface()
    network_interface.name = "global/networks/default"
    
    access_config = compute_v1.AccessConfig()
    access_config.type_ = compute_v1.AccessConfig.Type.ONE_TO_ONE_NAT
    access_config.name = "External NAT"
    network_interface.access_configs = [access_config]
    
    config.network_interfaces = [network_interface]
    
    # Create the instance
    request = compute_v1.InsertInstanceRequest()
    request.project = project_id
    request.zone = zone
    request.instance_resource = config
    
    operation = instance_client.insert(request=request)
    
    print(f"Creating instance {instance_name}...")
    
    # Wait for the operation to complete
    while operation.status != compute_v1.Operation.Status.DONE:
        time.sleep(1)
        operation = compute_v1.ZoneOperationsClient().get(
            project=project_id, zone=zone, operation=operation.name
        )
    
    print(f"Instance {instance_name} created successfully!")

# Usage
create_instance("your-project-id", "us-central1-a", "my-instance")
                '''
            },
            'storage': {
                'upload_blob': '''
from google.cloud import storage

def upload_blob(bucket_name: str, source_file_name: str, destination_blob_name: str):
    """Uploads a file to the bucket."""
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Upload the file
    blob.upload_from_filename(source_file_name)
    
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
    
    # Make the blob publicly viewable (optional)
    blob.make_public()
    print(f"Blob {destination_blob_name} is publicly accessible at {blob.public_url}")

# Usage
upload_blob("my-bucket", "local-file.txt", "storage-object-name.txt")
                ''',
                'list_blobs': '''
from google.cloud import storage

def list_blobs(bucket_name: str):
    """Lists all the blobs in the bucket."""
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # List all blobs in the bucket
    blobs = bucket.list_blobs()
    
    print(f"Blobs in bucket {bucket_name}:")
    for blob in blobs:
        print(f"  Name: {blob.name}")
        print(f"  Size: {blob.size} bytes")
        print(f"  Created: {blob.time_created}")
        print(f"  Updated: {blob.updated}")
        print("  ---")

# Usage
list_blobs("my-bucket")
                ''',
                'download_blob': '''
from google.cloud import storage

def download_blob(bucket_name: str, source_blob_name: str, destination_file_name: str):
    """Downloads a blob from the bucket."""
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    
    # Download the file
    blob.download_to_filename(destination_file_name)
    
    print(f"Downloaded {source_blob_name} to {destination_file_name}.")

# Usage
download_blob("my-bucket", "storage-object-name.txt", "local-file.txt")
                '''
            }
        }
        
        return examples.get(service, {}).get(operation, f"# Example for {service} {operation} not available")
    
    def get_service_recommendations(self, use_case: str) -> List[str]:
        """Get GCP service recommendations based on use case"""
        recommendations = {
            'web_application': [
                'Use App Engine for fully managed web hosting',
                'Use Cloud Load Balancing for traffic distribution',
                'Use Cloud SQL for relational database',
                'Use Cloud Storage for static assets',
                'Use Cloud CDN for global content delivery'
            ],
            'api_backend': [
                'Use Cloud Functions for serverless APIs',
                'Use API Gateway for API management',
                'Use Firestore for NoSQL database',
                'Use Identity and Access Management for authentication',
                'Use Cloud Monitoring for observability'
            ],
            'data_processing': [
                'Use Dataflow for stream and batch processing',
                'Use Dataprep for data preparation',
                'Use Pub/Sub for messaging and event streaming',
                'Use BigQuery for data warehousing',
                'Use Cloud Storage for data lake'
            ],
            'machine_learning': [
                'Use Vertex AI for ML platform',
                'Use AutoML for no-code ML models',
                'Use Cloud Functions for model serving',
                'Use AI Platform for custom training',
                'Use Cloud Monitoring for ML monitoring'
            ],
            'container_workloads': [
                'Use Google Kubernetes Engine (GKE)',
                'Use Cloud Run for containerized apps',
                'Use Artifact Registry for container images',
                'Use Cloud Build for CI/CD',
                'Use Cloud Monitoring for container monitoring'
            ]
        }
        
        return recommendations.get(use_case, [
            'Define your requirements more specifically',
            'Consider Google Cloud Architecture Framework',
            'Start with basic services and expand as needed'
        ])
    
    def get_gcloud_commands(self, service: str) -> List[str]:
        """Get common gcloud CLI commands for services"""
        commands = {
            'compute': [
                'gcloud compute instances list',
                'gcloud compute instances create INSTANCE_NAME --zone=ZONE',
                'gcloud compute instances start INSTANCE_NAME --zone=ZONE',
                'gcloud compute instances stop INSTANCE_NAME --zone=ZONE',
                'gcloud compute instances delete INSTANCE_NAME --zone=ZONE',
                'gcloud compute ssh INSTANCE_NAME --zone=ZONE'
            ],
            'storage': [
                'gsutil ls',
                'gsutil mb gs://BUCKET_NAME',
                'gsutil cp LOCAL_FILE gs://BUCKET_NAME/',
                'gsutil cp gs://BUCKET_NAME/OBJECT LOCAL_FILE',
                'gsutil rm gs://BUCKET_NAME/OBJECT',
                'gsutil rsync -r LOCAL_DIR gs://BUCKET_NAME/REMOTE_DIR'
            ],
            'functions': [
                'gcloud functions list',
                'gcloud functions deploy FUNCTION_NAME --runtime python39 --trigger-http',
                'gcloud functions call FUNCTION_NAME',
                'gcloud functions logs read FUNCTION_NAME',
                'gcloud functions delete FUNCTION_NAME'
            ],
            'kubernetes': [
                'gcloud container clusters list',
                'gcloud container clusters create CLUSTER_NAME',
                'gcloud container clusters get-credentials CLUSTER_NAME --zone=ZONE',
                'kubectl get nodes',
                'kubectl get pods',
                'kubectl apply -f deployment.yaml'
            ]
        }
        
        return commands.get(service, [f'# Commands for {service} not available'])


# Example usage
if __name__ == "__main__":
    gcp_helper = GCPHelper()
    
    # Generate Compute Terraform
    compute_config = {
        'name': 'web_server',
        'project_id': 'my-gcp-project',
        'region': 'us-west1',
        'zone': 'us-west1-a',
        'machine_type': 'e2-small',
        'environment': 'development'
    }
    
    print("GCP Compute Terraform Configuration:")
    print(gcp_helper.generate_terraform_compute(compute_config))
    
    print("\n" + "="*50 + "\n")
    
    # Get recommendations
    print("Web Application Recommendations:")
    for rec in gcp_helper.get_service_recommendations('web_application'):
        print(f"- {rec}")
    
    print("\n" + "="*30 + "\n")
    
    # Get gcloud commands
    print("Common Compute Commands:")
    for cmd in gcp_helper.get_gcloud_commands('compute'):
        print(f"- {cmd}")