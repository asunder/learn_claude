# Hypervisor & Cloud Infrastructure Code Helper Agent

A specialized Claude agent designed to assist with hypervisor and cloud infrastructure programming tasks across AWS, Azure, and Google Cloud Platform.

## Features

- **Multi-Cloud Support**: AWS, Azure, and GCP specific helpers
- **Infrastructure as Code**: Generate Terraform configurations, CloudFormation templates, ARM templates
- **Code Generation**: Create SDK examples, Lambda functions, Azure Functions, Cloud Functions  
- **Best Practices**: Provides recommendations based on use cases
- **Hypervisor Support**: VMware, Hyper-V, KVM guidance

## Quick Start

```python
from hypervisor_agent import HypervisorAgent

# Initialize the agent
agent = HypervisorAgent()

# Get help with a specific query
result = agent.suggest_solution("How do I create a Terraform configuration for AWS EC2?", "aws")
print(result['recommendations'])
print(result['code_examples'][0])
```

## Cloud-Specific Helpers

### AWS Helper

```python
from aws_helper import AWSHelper

aws = AWSHelper()

# Generate EC2 Terraform configuration
config = {
    'name': 'web_server',
    'instance_type': 't3.micro',
    'ami': 'ami-0abcdef1234567890'
}
terraform_code = aws.generate_terraform_ec2(config)

# Get service recommendations
recommendations = aws.get_service_recommendations('web_application')

# Generate boto3 examples
code = aws.generate_boto3_example('ec2', 'list_instances')
```

### Azure Helper

```python
from azure_helper import AzureHelper

azure = AzureHelper()

# Generate VM Terraform configuration
config = {
    'name': 'web_vm',
    'location': 'East US',
    'vm_size': 'Standard_B1s'
}
terraform_code = azure.generate_terraform_vm(config)

# Generate Azure SDK examples
code = azure.generate_azure_sdk_example('compute', 'list_vms')
```

### GCP Helper

```python
from gcp_helper import GCPHelper

gcp = GCPHelper()

# Generate Compute Engine Terraform
config = {
    'name': 'web_instance',
    'project_id': 'my-project',
    'machine_type': 'e2-micro'
}
terraform_code = gcp.generate_terraform_compute(config)

# Get gcloud commands
commands = gcp.get_gcloud_commands('compute')
```

## Supported Use Cases

The agent provides specialized recommendations for:

- **Web Applications**: Load balancing, databases, static assets
- **API Backends**: Serverless functions, authentication, monitoring  
- **Data Processing**: ETL pipelines, streaming, analytics
- **Machine Learning**: Training workflows, model serving
- **Container Workloads**: Kubernetes, container registries

## Available Help Categories

1. Infrastructure as Code
2. Virtual Machine Management
3. Container Orchestration
4. Network Configuration
5. Storage Management
6. Security and Compliance
7. Monitoring and Logging
8. Cost Optimization
9. Migration Strategies

## Code Generation Examples

### Terraform EC2 Instance (AWS)
```hcl
# AWS EC2 Instance Configuration
resource "aws_instance" "web_server" {
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"
  key_name      = "my-key-pair"
  
  vpc_security_group_ids = [aws_security_group.web_server_sg.id]
  subnet_id              = "subnet-12345678"
  
  tags = {
    Name        = "Web Server"
    Environment = "production"
  }
}
```

### Azure VM Terraform
```hcl
# Azure Virtual Machine
resource "azurerm_linux_virtual_machine" "example" {
  name                = "example-vm"
  resource_group_name = azurerm_resource_group.example.name
  location            = azurerm_resource_group.example.location
  size                = "Standard_B1s"
  admin_username      = "adminuser"
}
```

### GCP Compute Instance
```hcl
# GCP Compute instance
resource "google_compute_instance" "example" {
  name         = "web-instance"
  machine_type = "e2-micro"
  zone         = "us-central1-a"
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }
}
```

## Testing

Run the simple test to verify functionality:

```bash
python simple_test.py
```

For comprehensive testing (requires fixing template issues):

```bash
python test_agent.py
```

## Files Structure

- `hypervisor_agent.py` - Main agent class with multi-cloud support
- `aws_helper.py` - AWS-specific code generation and helpers
- `azure_helper.py` - Azure-specific code generation and helpers  
- `gcp_helper.py` - GCP-specific code generation and helpers
- `config.py` - Configuration, templates, and best practices
- `simple_test.py` - Basic functionality test
- `test_agent.py` - Comprehensive test suite

## Supported Cloud Services

### AWS
- EC2, Lambda, ECS, EKS, S3, RDS, VPC, CloudFront, Route53

### Azure
- Virtual Machines, Functions, AKS, Storage, SQL Database, VNet

### GCP
- Compute Engine, Cloud Functions, GKE, Cloud Storage, Cloud SQL

## Best Practices Integration

The agent includes built-in best practices for:

- **Security**: IAM roles, encryption, least privilege
- **Performance**: Right-sizing, auto-scaling, caching
- **Cost Optimization**: Reserved instances, lifecycle policies
- **Reliability**: Multi-AZ deployment, health checks, backups

## Contributing

To extend the agent:

1. Add new cloud providers in the respective helper files
2. Update configuration templates in `config.py`
3. Add test cases in `test_agent.py`
4. Update this README with new capabilities

## License

This project is provided as-is for educational and development purposes.