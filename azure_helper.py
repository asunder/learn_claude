"""
Azure-specific helper functions and code generators
"""

from typing import Dict, List, Any
import json


class AzureHelper:
    """Azure-specific helper for infrastructure and code assistance"""
    
    def __init__(self):
        self.services = {
            'compute': ['Virtual Machines', 'Container Instances', 'AKS', 'Functions', 'Batch'],
            'storage': ['Storage Accounts', 'Blob Storage', 'File Storage', 'Disk Storage'],
            'database': ['SQL Database', 'Cosmos DB', 'Database for MySQL', 'Database for PostgreSQL'],
            'networking': ['Virtual Network', 'Load Balancer', 'Application Gateway', 'Traffic Manager'],
            'security': ['Active Directory', 'Key Vault', 'Security Center', 'Sentinel'],
            'monitoring': ['Monitor', 'Application Insights', 'Log Analytics']
        }
    
    def generate_terraform_vm(self, config: Dict[str, Any]) -> str:
        """Generate Terraform configuration for Azure VM"""
        template = f'''
# Azure Resource Group
resource "azurerm_resource_group" "{config.get('name', 'example')}" {
  name     = "{config.get('resource_group', 'rg-' + config.get('name', 'example'))}"
  location = "{config.get('location', 'East US')}"
  
  tags = {
    Environment = "{config.get('environment', 'production')}"
    Project     = "{config.get('project', 'default')}"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "{config.get('name', 'example')}_vnet" {
  name                = "{config.get('name', 'example')}-vnet"
  address_space       = ["{config.get('vnet_cidr', '10.0.0.0/16')}"]
  location            = azurerm_resource_group.{config.get('name', 'example')}.location
  resource_group_name = azurerm_resource_group.{config.get('name', 'example')}.name
  
  tags = {
    Environment = "{config.get('environment', 'production')}"
  }
}

# Subnet
resource "azurerm_subnet" "{config.get('name', 'example')}_subnet" {
  name                 = "{config.get('name', 'example')}-subnet"
  resource_group_name  = azurerm_resource_group.{config.get('name', 'example')}.name
  virtual_network_name = azurerm_virtual_network.{config.get('name', 'example')}_vnet.name
  address_prefixes     = ["{config.get('subnet_cidr', '10.0.1.0/24')}"]
}

# Network Security Group
resource "azurerm_network_security_group" "{config.get('name', 'example')}_nsg" {
  name                = "{config.get('name', 'example')}-nsg"
  location            = azurerm_resource_group.{config.get('name', 'example')}.location
  resource_group_name = azurerm_resource_group.{config.get('name', 'example')}.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "{config.get('ssh_source', '10.0.0.0/8')}"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "HTTP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  tags = {
    Environment = "{config.get('environment', 'production')}"
  }
}

# Public IP
resource "azurerm_public_ip" "{config.get('name', 'example')}_pip" {
  name                = "{config.get('name', 'example')}-pip"
  resource_group_name = azurerm_resource_group.{config.get('name', 'example')}.name
  location            = azurerm_resource_group.{config.get('name', 'example')}.location
  allocation_method   = "Static"
  sku                = "Standard"
  
  tags = {
    Environment = "{config.get('environment', 'production')}"
  }
}

# Network Interface
resource "azurerm_network_interface" "{config.get('name', 'example')}_nic" {
  name                = "{config.get('name', 'example')}-nic"
  location            = azurerm_resource_group.{config.get('name', 'example')}.location
  resource_group_name = azurerm_resource_group.{config.get('name', 'example')}.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.{config.get('name', 'example')}_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.{config.get('name', 'example')}_pip.id
  }
  
  tags = {
    Environment = "{config.get('environment', 'production')}"
  }
}

# Associate Network Security Group to Network Interface
resource "azurerm_network_interface_security_group_association" "{config.get('name', 'example')}" {
  network_interface_id      = azurerm_network_interface.{config.get('name', 'example')}_nic.id
  network_security_group_id = azurerm_network_security_group.{config.get('name', 'example')}_nsg.id
}

# Virtual Machine
resource "azurerm_linux_virtual_machine" "{config.get('name', 'example')}" {
  name                = "{config.get('display_name', config.get('name', 'example'))}"
  resource_group_name = azurerm_resource_group.{config.get('name', 'example')}.name
  location            = azurerm_resource_group.{config.get('name', 'example')}.location
  size                = "{config.get('vm_size', 'Standard_B1s')}"
  admin_username      = "{config.get('admin_username', 'adminuser')}"

  disable_password_authentication = true

  network_interface_ids = [
    azurerm_network_interface.{config.get('name', 'example')}_nic.id,
  ]

  admin_ssh_key {
    username   = "{config.get('admin_username', 'adminuser')}"
    public_key = file("{config.get('ssh_key_path', '~/.ssh/id_rsa.pub')}")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "{config.get('disk_type', 'Standard_LRS')}"
  }

  source_image_reference {
    publisher = "{config.get('image_publisher', 'Canonical')}"
    offer     = "{config.get('image_offer', '0001-com-ubuntu-server-jammy')}"
    sku       = "{config.get('image_sku', '22_04-lts')}"
    version   = "{config.get('image_version', 'latest')}"
  }
  
  tags = {
    Name        = "{config.get('display_name', config.get('name', 'example'))}"
    Environment = "{config.get('environment', 'production')}"
  }
}
        '''
        return template.strip()
    
    def generate_arm_template(self, config: Dict[str, Any]) -> str:
        """Generate ARM template for basic infrastructure"""
        template = {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {
                "vmName": {
                    "type": "string",
                    "defaultValue": config.get('vm_name', 'myVM'),
                    "metadata": {
                        "description": "Name of the virtual machine"
                    }
                },
                "adminUsername": {
                    "type": "string",
                    "defaultValue": config.get('admin_username', 'adminuser'),
                    "metadata": {
                        "description": "Admin username for the VM"
                    }
                },
                "vmSize": {
                    "type": "string",
                    "defaultValue": config.get('vm_size', 'Standard_B1s'),
                    "metadata": {
                        "description": "Size of the VM"
                    }
                }
            },
            "variables": {
                "vnetName": f"[concat(parameters('vmName'), '-vnet')]",
                "subnetName": "default",
                "nsgName": f"[concat(parameters('vmName'), '-nsg')]",
                "publicIPName": f"[concat(parameters('vmName'), '-pip')]",
                "nicName": f"[concat(parameters('vmName'), '-nic')]"
            },
            "resources": [
                {
                    "type": "Microsoft.Network/virtualNetworks",
                    "apiVersion": "2020-06-01",
                    "name": "[variables('vnetName')]",
                    "location": "[resourceGroup().location]",
                    "properties": {
                        "addressSpace": {
                            "addressPrefixes": [
                                config.get('vnet_cidr', '10.0.0.0/16')
                            ]
                        },
                        "subnets": [
                            {
                                "name": "[variables('subnetName')]",
                                "properties": {
                                    "addressPrefix": config.get('subnet_cidr', '10.0.0.0/24')
                                }
                            }
                        ]
                    }
                },
                {
                    "type": "Microsoft.Network/networkSecurityGroups",
                    "apiVersion": "2020-06-01",
                    "name": "[variables('nsgName')]",
                    "location": "[resourceGroup().location]",
                    "properties": {
                        "securityRules": [
                            {
                                "name": "SSH",
                                "properties": {
                                    "priority": 1001,
                                    "protocol": "TCP",
                                    "access": "Allow",
                                    "direction": "Inbound",
                                    "sourceAddressPrefix": "*",
                                    "sourcePortRange": "*",
                                    "destinationAddressPrefix": "*",
                                    "destinationPortRange": "22"
                                }
                            }
                        ]
                    }
                },
                {
                    "type": "Microsoft.Compute/virtualMachines",
                    "apiVersion": "2020-06-01",
                    "name": "[parameters('vmName')]",
                    "location": "[resourceGroup().location]",
                    "dependsOn": [
                        f"[resourceId('Microsoft.Network/networkInterfaces', variables('nicName'))]"
                    ],
                    "properties": {
                        "hardwareProfile": {
                            "vmSize": "[parameters('vmSize')]"
                        },
                        "osProfile": {
                            "computerName": "[parameters('vmName')]",
                            "adminUsername": "[parameters('adminUsername')]",
                            "linuxConfiguration": {
                                "disablePasswordAuthentication": True,
                                "ssh": {
                                    "publicKeys": [
                                        {
                                            "path": f"[concat('/home/', parameters('adminUsername'), '/.ssh/authorized_keys')]",
                                            "keyData": config.get('ssh_public_key', 'YOUR_SSH_PUBLIC_KEY_HERE')
                                        }
                                    ]
                                }
                            }
                        },
                        "storageProfile": {
                            "imageReference": {
                                "publisher": "Canonical",
                                "offer": "0001-com-ubuntu-server-jammy", 
                                "sku": "22_04-lts",
                                "version": "latest"
                            },
                            "osDisk": {
                                "createOption": "FromImage",
                                "managedDisk": {
                                    "storageAccountType": "Standard_LRS"
                                }
                            }
                        },
                        "networkProfile": {
                            "networkInterfaces": [
                                {
                                    "id": f"[resourceId('Microsoft.Network/networkInterfaces', variables('nicName'))]"
                                }
                            ]
                        }
                    }
                }
            ],
            "outputs": {
                "vmName": {
                    "type": "string",
                    "value": "[parameters('vmName')]"
                },
                "publicIPAddress": {
                    "type": "string", 
                    "value": f"[reference(resourceId('Microsoft.Network/publicIPAddresses', variables('publicIPName'))).ipAddress]"
                }
            }
        }
        
        return json.dumps(template, indent=2)
    
    def generate_azure_function(self, config: Dict[str, Any]) -> str:
        """Generate Azure Function code"""
        runtime = config.get('runtime', 'python')
        
        if runtime == 'python':
            return f'''
import azure.functions as func
import json
import logging
from typing import Dict, Any

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function: {config.get('description', 'Generated Azure Function')}
    """
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get request data
        req_body = req.get_json() if req.get_json() else {}
        
        # Your business logic here
        logging.info(f'Request body: {json.dumps(req_body)}')
        
        response_data = {
            "message": "Function executed successfully",
            "input": req_body,
            "status": "success"
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers={
                "Content-Type": "application/json"
            }
        )
        
    except Exception as e:
        logging.error(f'Error in function execution: {str(e)}')
        
        error_response = {
            "error": str(e),
            "status": "error"
        }
        
        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            headers={
                "Content-Type": "application/json"
            }
        )

# Function configuration (function.json)
function_json = {
    "scriptFile": "__init__.py",
    "bindings": [
        {
            "authLevel": "{config.get('auth_level', 'function')}",
            "type": "httpTrigger",
            "direction": "in",
            "name": "req",
            "methods": [
                "get",
                "post"
            ]
        },
        {
            "type": "http",
            "direction": "out",
            "name": "$return"
        }
    ]
}
            '''
        
        elif runtime == 'javascript':
            return f'''
module.exports = async function (context, req) {
    context.log('JavaScript HTTP trigger function processed a request.');

    try {
        const requestBody = req.body || {};
        
        // Your business logic here
        context.log('Request body:', JSON.stringify(requestBody));
        
        const responseData = {
            message: 'Function executed successfully',
            input: requestBody,
            status: 'success'
        };
        
        context.res = {
            status: 200,
            headers: {
                'Content-Type': 'application/json'
            },
            body: responseData
        };
        
    } catch (error) {
        context.log.error('Error in function execution:', error);
        
        context.res = {
            status: 500,
            headers: {
                'Content-Type': 'application/json'
            },
            body: {
                error: error.message,
                status: 'error'
            }
        };
    }
};
            '''
    
    def generate_azure_sdk_example(self, service: str, operation: str) -> str:
        """Generate Azure SDK code examples"""
        examples = {
            'compute': {
                'list_vms': '''
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

credential = DefaultAzureCredential()
subscription_id = "your-subscription-id"

compute_client = ComputeManagementClient(credential, subscription_id)

# List all VMs in subscription
for vm in compute_client.virtual_machines.list_all():
    print(f"VM Name: {vm.name}")
    print(f"Location: {vm.location}")
    print(f"VM Size: {vm.hardware_profile.vm_size}")
    print("---")
                ''',
                'create_vm': '''
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient

credential = DefaultAzureCredential()
subscription_id = "your-subscription-id"
resource_group_name = "my-resource-group"
vm_name = "my-vm"

compute_client = ComputeManagementClient(credential, subscription_id)

vm_parameters = {
    'location': 'East US',
    'os_profile': {
        'computer_name': vm_name,
        'admin_username': 'adminuser',
        'linux_configuration': {
            'disable_password_authentication': True,
            'ssh': {
                'public_keys': [{
                    'path': '/home/adminuser/.ssh/authorized_keys',
                    'key_data': 'your-ssh-public-key'
                }]
            }
        }
    },
    'hardware_profile': {
        'vm_size': 'Standard_B1s'
    },
    'storage_profile': {
        'image_reference': {
            'publisher': 'Canonical',
            'offer': '0001-com-ubuntu-server-jammy',
            'sku': '22_04-lts',
            'version': 'latest'
        }
    },
    'network_profile': {
        'network_interfaces': [{
            'id': '/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/networkInterfaces/{vm_name}-nic'
        }]
    }
}

async_vm_creation = compute_client.virtual_machines.begin_create_or_update(
    resource_group_name, vm_name, vm_parameters
)
vm_result = async_vm_creation.result()

print(f"VM {vm_result.name} created successfully")
                '''
            },
            'storage': {
                'upload_blob': '''
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
account_url = "https://yourstorageaccount.blob.core.windows.net"

blob_service_client = BlobServiceClient(account_url, credential=credential)
container_name = "mycontainer"
blob_name = "myblob.txt"
data = "Hello, Azure Blob Storage!"

# Upload blob
blob_client = blob_service_client.get_blob_client(
    container=container_name, 
    blob=blob_name
)

blob_client.upload_blob(data, overwrite=True)
print(f"Blob {blob_name} uploaded successfully")
                ''',
                'list_blobs': '''
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
account_url = "https://yourstorageaccount.blob.core.windows.net"

blob_service_client = BlobServiceClient(account_url, credential=credential)
container_name = "mycontainer"

container_client = blob_service_client.get_container_client(container_name)

# List blobs in container
for blob in container_client.list_blobs():
    print(f"Blob name: {blob.name}")
    print(f"Size: {blob.size} bytes")
    print(f"Last modified: {blob.last_modified}")
    print("---")
                '''
            }
        }
        
        return examples.get(service, {}).get(operation, f"# Example for {service} {operation} not available")
    
    def get_service_recommendations(self, use_case: str) -> List[str]:
        """Get Azure service recommendations based on use case"""
        recommendations = {
            'web_application': [
                'Use App Service for web hosting',
                'Use Application Gateway for load balancing',
                'Use Azure SQL Database for relational data',
                'Use Storage Account for static files',
                'Use CDN for global content delivery'
            ],
            'api_backend': [
                'Use Azure Functions for serverless APIs',
                'Use API Management for API gateway',
                'Use Cosmos DB for NoSQL database',
                'Use Active Directory B2C for authentication',
                'Use Application Insights for monitoring'
            ],
            'data_processing': [
                'Use HDInsight for big data processing',
                'Use Data Factory for ETL pipelines',
                'Use Event Hubs for streaming data',
                'Use Data Lake Storage for data lake',
                'Use Synapse Analytics for data warehousing'
            ],
            'machine_learning': [
                'Use Machine Learning service for ML workflows',
                'Use Cognitive Services for pre-built AI',
                'Use Container Instances for model serving',
                'Use Batch for training workloads',
                'Use Monitor for model performance tracking'
            ]
        }
        
        return recommendations.get(use_case, [
            'Define your requirements more specifically',
            'Consider Azure Architecture Center patterns',
            'Start with basic services and expand as needed'
        ])


# Example usage
if __name__ == "__main__":
    azure_helper = AzureHelper()
    
    # Generate VM Terraform
    vm_config = {
        'name': 'web_server',
        'location': 'East US',
        'vm_size': 'Standard_B2s',
        'environment': 'development'
    }
    
    print("Azure VM Terraform Configuration:")
    print(azure_helper.generate_terraform_vm(vm_config))
    
    print("\n" + "="*50 + "\n")
    
    # Get recommendations
    print("Web Application Recommendations:")
    for rec in azure_helper.get_service_recommendations('web_application'):
        print(f"- {rec}")