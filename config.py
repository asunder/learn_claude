"""
Configuration file for the Hypervisor Agent
"""

# Agent Configuration
AGENT_CONFIG = {
    "name": "HypervisorAgent",
    "version": "1.0.0",
    "description": "Specialized assistant for hypervisor and cloud infrastructure programming tasks",
    "supported_languages": ["python", "javascript", "go", "terraform", "yaml", "json", "powershell", "bash"],
    "specialties": [
        "Infrastructure as Code",
        "Cloud Architecture",
        "Hypervisor Management", 
        "Container Orchestration",
        "DevOps Automation"
    ]
}

# Cloud Provider Templates
CLOUD_TEMPLATES = {
    "aws": {
        "ec2_basic": """
# Basic EC2 instance
resource "aws_instance" "example" {
  ami           = var.ami_id
  instance_type = var.instance_type
  
  tags = {
    Name = var.instance_name
  }
}
        """,
        "vpc_basic": """
# Basic VPC setup
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "main-vpc"
  }
}
        """
    },
    "azure": {
        "vm_basic": """
# Basic Azure VM
resource "azurerm_linux_virtual_machine" "example" {
  name                = var.vm_name
  resource_group_name = var.resource_group_name
  location            = var.location
  size                = "Standard_B1s"
  admin_username      = "adminuser"
  
  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
}
        """,
        "resource_group": """
# Azure Resource Group
resource "azurerm_resource_group" "example" {
  name     = var.resource_group_name
  location = var.location
}
        """
    },
    "gcp": {
        "compute_basic": """
# Basic GCP Compute instance
resource "google_compute_instance" "example" {
  name         = var.instance_name
  machine_type = "e2-micro"
  zone         = var.zone
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }
  
  network_interface {
    network = "default"
  }
}
        """
    }
}

# Common Code Snippets
CODE_SNIPPETS = {
    "kubernetes": {
        "deployment": """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app_name }}
spec:
  replicas: {{ replica_count }}
  selector:
    matchLabels:
      app: {{ app_name }}
  template:
    metadata:
      labels:
        app: {{ app_name }}
    spec:
      containers:
      - name: {{ container_name }}
        image: {{ image_name }}
        ports:
        - containerPort: {{ port }}
        """,
        "service": """
apiVersion: v1
kind: Service
metadata:
  name: {{ service_name }}
spec:
  selector:
    app: {{ app_name }}
  ports:
    - protocol: TCP
      port: {{ service_port }}
      targetPort: {{ target_port }}
  type: {{ service_type }}
        """
    },
    "docker": {
        "dockerfile": """
FROM {{ base_image }}

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE {{ port }}

CMD ["{{ start_command }}"]
        """,
        "docker_compose": """
version: '3.8'
services:
  {{ service_name }}:
    build: .
    ports:
      - "{{ host_port }}:{{ container_port }}"
    environment:
      - ENV=production
    volumes:
      - ./data:/app/data
        """
    }
}

# Best Practices by Category
BEST_PRACTICES = {
    "security": [
        "Use IAM roles instead of hardcoded credentials",
        "Enable encryption at rest and in transit", 
        "Implement least privilege access principles",
        "Use secrets management services (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)",
        "Enable logging and monitoring for security events"
    ],
    "performance": [
        "Choose appropriate instance types for workload",
        "Use auto-scaling groups for variable workloads",
        "Implement caching strategies",
        "Optimize network topology and routing",
        "Monitor resource utilization"
    ],
    "cost_optimization": [
        "Use reserved instances for predictable workloads",
        "Implement lifecycle policies for storage",
        "Right-size instances based on actual usage",
        "Use spot instances for fault-tolerant workloads",
        "Implement cost monitoring and alerts"
    ],
    "reliability": [
        "Design for multiple availability zones",
        "Implement health checks and monitoring",
        "Use infrastructure as code for consistency",
        "Plan for disaster recovery",
        "Implement automated backups"
    ]
}

# Command References
COMMAND_REFERENCES = {
    "aws_cli": {
        "ec2": [
            "aws ec2 describe-instances",
            "aws ec2 start-instances --instance-ids i-1234567890abcdef0",
            "aws ec2 stop-instances --instance-ids i-1234567890abcdef0",
            "aws ec2 create-tags --resources i-1234567890abcdef0 --tags Key=Name,Value=MyInstance"
        ],
        "s3": [
            "aws s3 ls",
            "aws s3 cp file.txt s3://mybucket/",
            "aws s3 sync ./local-folder s3://mybucket/remote-folder"
        ]
    },
    "azure_cli": {
        "vm": [
            "az vm list",
            "az vm start --name MyVM --resource-group MyResourceGroup",
            "az vm stop --name MyVM --resource-group MyResourceGroup"
        ],
        "storage": [
            "az storage account list",
            "az storage blob upload --file myfile.txt --name myblob --account-name mystorageaccount"
        ]
    },
    "gcp_cli": {
        "compute": [
            "gcloud compute instances list",
            "gcloud compute instances start INSTANCE_NAME --zone=ZONE",
            "gcloud compute instances stop INSTANCE_NAME --zone=ZONE"
        ],
        "storage": [
            "gsutil ls",
            "gsutil cp file.txt gs://mybucket/",
            "gsutil rsync -r ./local-dir gs://mybucket/remote-dir"
        ]
    }
}