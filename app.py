#!/usr/bin/env python3
"""
Flask web application for the Hypervisor Agent learning platform
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import traceback
from hypervisor_agent import HypervisorAgent
from aws_helper import AWSHelper
from azure_helper import AzureHelper
from gcp_helper import GCPHelper

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize helpers
agent = HypervisorAgent()
aws_helper = AWSHelper()
azure_helper = AzureHelper()
gcp_helper = GCPHelper()

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

@app.route('/aws')
def aws_page():
    """AWS-specific page"""
    return render_template('aws.html', 
                         services=aws_helper.services,
                         use_cases=['web_application', 'api_backend', 'data_processing', 'machine_learning'])

@app.route('/azure')  
def azure_page():
    """Azure-specific page"""
    return render_template('azure.html',
                         services=azure_helper.services,
                         use_cases=['web_application', 'api_backend', 'data_processing', 'machine_learning'])

@app.route('/gcp')
def gcp_page():
    """GCP-specific page"""
    return render_template('gcp.html',
                         services=gcp_helper.services,
                         use_cases=['web_application', 'api_backend', 'data_processing', 'machine_learning', 'container_workloads'])

@app.route('/terraform')
def terraform_page():
    """Terraform code generation page"""
    return render_template('terraform.html')

@app.route('/generate_terraform', methods=['POST'])
def generate_terraform():
    """Generate Terraform code based on user input"""
    try:
        provider = request.form.get('provider')
        resource_type = request.form.get('resource_type')
        
        # Get configuration from form
        config = {}
        for key, value in request.form.items():
            if key not in ['provider', 'resource_type'] and value.strip():
                config[key] = value.strip()
        
        # Generate code based on provider and resource type
        if provider == 'aws' and resource_type == 'ec2':
            code = aws_helper.generate_terraform_ec2(config)
        elif provider == 'azure' and resource_type == 'vm':
            # Note: Azure helper has template issues, provide simple example
            code = f'''# Azure VM Terraform (simplified)
resource "azurerm_linux_virtual_machine" "{config.get('name', 'example')}" {{
  name                = "{config.get('name', 'example-vm')}"
  resource_group_name = "{config.get('resource_group', 'example-rg')}"
  location            = "{config.get('location', 'East US')}"
  size                = "{config.get('vm_size', 'Standard_B1s')}"
  admin_username      = "{config.get('admin_username', 'adminuser')}"
}}'''
        elif provider == 'gcp' and resource_type == 'compute':
            code = gcp_helper.generate_terraform_compute(config)
        else:
            code = "# Unsupported provider/resource combination"
        
        return jsonify({
            'success': True,
            'code': code,
            'provider': provider,
            'resource_type': resource_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()})

@app.route('/sdk_examples')
def sdk_examples():
    """SDK code examples page"""
    return render_template('sdk_examples.html')

@app.route('/generate_sdk', methods=['POST'])
def generate_sdk():
    """Generate SDK code examples"""
    try:
        provider = request.form.get('provider')
        service = request.form.get('service')
        operation = request.form.get('operation')
        
        if provider == 'aws':
            code = aws_helper.generate_boto3_example(service, operation)
        elif provider == 'azure':
            code = azure_helper.generate_azure_sdk_example(service, operation)
        elif provider == 'gcp':
            code = gcp_helper.generate_gcp_sdk_example(service, operation)
        else:
            code = "# Unsupported provider"
        
        return jsonify({
            'success': True,
            'code': code,
            'provider': provider,
            'service': service,
            'operation': operation
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/recommendations/<use_case>')
def recommendations(use_case):
    """Get recommendations for a specific use case"""
    try:
        aws_recs = aws_helper.get_service_recommendations(use_case)
        azure_recs = azure_helper.get_service_recommendations(use_case) 
        gcp_recs = gcp_helper.get_service_recommendations(use_case)
        
        return jsonify({
            'use_case': use_case,
            'aws': aws_recs,
            'azure': azure_recs,
            'gcp': gcp_recs
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/best_practices')
def best_practices():
    """Best practices page"""
    from config import BEST_PRACTICES
    return render_template('best_practices.html', practices=BEST_PRACTICES)

@app.route('/hypervisors')
def hypervisors():
    """Hypervisor information page"""
    return render_template('hypervisors.html', hypervisors=agent.hypervisors)

@app.route('/api/search')
def search_api():
    """API endpoint for searching capabilities"""
    query = request.args.get('q', '').lower()
    results = []
    
    # Search through help categories
    for category in agent.get_help_categories():
        if query in category.lower():
            results.append({
                'type': 'category',
                'title': category,
                'description': f'Help with {category.lower()}'
            })
    
    # Search through cloud providers
    for key, provider in agent.cloud_providers.items():
        if query in provider.name.lower() or query in key:
            results.append({
                'type': 'provider',
                'title': provider.name,
                'description': f'Services: {", ".join(provider.services[:3])}...',
                'url': f'/{key}'
            })
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)