#!/usr/bin/env python3
"""
Simple Flask web application for the Hypervisor Agent learning platform
"""

from flask import Flask, render_template, request, jsonify
import json
import traceback
from hypervisor_agent import HypervisorAgent
from config import BEST_PRACTICES

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize agent
agent = HypervisorAgent()

@app.route('/')
def index():
    """Home page with overview"""
    return render_template('index.html', 
                         cloud_providers=agent.cloud_providers,
                         help_categories=agent.get_help_categories(),
                         hypervisors=agent.hypervisors)

@app.route('/query', methods=['GET', 'POST'])
def query_agent():
    """Interactive query interface"""
    if request.method == 'GET':
        return render_template('query.html')
    
    try:
        query = request.form.get('query', '').strip()
        provider = request.form.get('provider', '').strip()
        
        if not query:
            return jsonify({'error': 'Please enter a query'})
        
        # Get suggestions from agent
        result = agent.suggest_solution(query, provider if provider != 'auto' else None)
        
        return jsonify({
            'success': True,
            'query': result['query'],
            'provider': result['provider'] or 'General',
            'recommendations': result['recommendations'],
            'code_examples': result['code_examples']
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()})

@app.route('/terraform')
def terraform_page():
    """Terraform code generation page"""
    return render_template('terraform.html')

@app.route('/generate_terraform', methods=['POST'])
def generate_terraform():
    """Generate Terraform code based on user input (simplified)"""
    try:
        provider = request.form.get('provider')
        resource_type = request.form.get('resource_type')
        name = request.form.get('name', 'example')
        
        # Simple templates without complex f-string issues
        if provider == 'aws' and resource_type == 'ec2':
            code = f'''# AWS EC2 Instance
resource "aws_instance" "{name}" {{
  ami           = "ami-0c55b159cbfafe1d0"
  instance_type = "t2.micro"
  
  tags = {{
    Name = "{name}"
  }}
}}'''
        elif provider == 'azure' and resource_type == 'vm':
            code = f'''# Azure Virtual Machine
resource "azurerm_linux_virtual_machine" "{name}" {{
  name                = "{name}"
  resource_group_name = "example-rg"
  location            = "East US"
  size                = "Standard_B1s"
  admin_username      = "adminuser"
}}'''
        elif provider == 'gcp' and resource_type == 'compute':
            code = f'''# GCP Compute Instance  
resource "google_compute_instance" "{name}" {{
  name         = "{name}"
  machine_type = "e2-micro"
  zone         = "us-central1-a"
  
  boot_disk {{
    initialize_params {{
      image = "debian-cloud/debian-11"
    }}
  }}
}}'''
        else:
            code = "# Please select a valid provider and resource type"
        
        return jsonify({
            'success': True,
            'code': code,
            'provider': provider,
            'resource_type': resource_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/sdk_examples')
def sdk_examples():
    """SDK code examples page"""
    return render_template('sdk_examples.html')

@app.route('/generate_sdk', methods=['POST'])
def generate_sdk():
    """Generate SDK code examples (simplified)"""
    try:
        provider = request.form.get('provider')
        service = request.form.get('service')
        operation = request.form.get('operation')
        
        # Simple SDK examples
        examples = {
            'aws': {
                'ec2': {
                    'list_instances': '''import boto3

ec2 = boto3.client('ec2')
response = ec2.describe_instances()

for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        print(f"Instance ID: {instance['InstanceId']}")
        print(f"State: {instance['State']['Name']}")''',
                    'create_instance': '''import boto3

ec2 = boto3.client('ec2')
response = ec2.run_instances(
    ImageId='ami-0c55b159cbfafe1d0',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro'
)

print(f"Instance created: {response['Instances'][0]['InstanceId']}")'''
                },
                's3': {
                    'upload_file': '''import boto3

s3 = boto3.client('s3')
s3.upload_file('local_file.txt', 'my-bucket', 'remote_file.txt')
print("File uploaded successfully")''',
                    'list_objects': '''import boto3

s3 = boto3.client('s3')
response = s3.list_objects_v2(Bucket='my-bucket')

for obj in response.get('Contents', []):
    print(f"Key: {obj['Key']}")
    print(f"Size: {obj['Size']} bytes")'''
                }
            }
        }
        
        code = examples.get(provider, {}).get(service, {}).get(operation, f"# Example for {provider} {service} {operation} not available")
        
        return jsonify({
            'success': True,
            'code': code,
            'provider': provider,
            'service': service,
            'operation': operation
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/best_practices')
def best_practices():
    """Best practices page"""
    return render_template('best_practices.html', practices=BEST_PRACTICES)

@app.route('/aws')
def aws_page():
    """AWS-specific page"""
    return render_template('aws.html')

@app.route('/azure')  
def azure_page():
    """Azure-specific page"""
    return render_template('azure.html')

@app.route('/gcp')
def gcp_page():
    """GCP-specific page"""
    return render_template('gcp.html')

@app.route('/hypervisors')
def hypervisors():
    """Hypervisor information page"""
    return render_template('hypervisors.html', hypervisors=agent.hypervisors)

@app.route('/recommendations/<use_case>')
def recommendations(use_case):
    """Get recommendations for a specific use case (simplified)"""
    try:
        # Simple recommendations without helper classes
        recs = {
            'web_application': {
                'aws': ['Use EC2 for compute', 'Use ALB for load balancing', 'Use RDS for database'],
                'azure': ['Use App Service for hosting', 'Use Application Gateway', 'Use SQL Database'],
                'gcp': ['Use App Engine', 'Use Cloud Load Balancing', 'Use Cloud SQL']
            },
            'api_backend': {
                'aws': ['Use Lambda for serverless', 'Use API Gateway', 'Use DynamoDB'],
                'azure': ['Use Functions', 'Use API Management', 'Use Cosmos DB'],
                'gcp': ['Use Cloud Functions', 'Use API Gateway', 'Use Firestore']
            }
        }
        
        result = recs.get(use_case, {
            'aws': ['Define requirements more specifically'],
            'azure': ['Define requirements more specifically'], 
            'gcp': ['Define requirements more specifically']
        })
        
        return jsonify({
            'use_case': use_case,
            'aws': result.get('aws', []),
            'azure': result.get('azure', []),
            'gcp': result.get('gcp', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)