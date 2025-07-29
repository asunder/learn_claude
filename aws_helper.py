"""
AWS-specific helper functions and code generators
"""

from typing import Dict, List, Any
import json


class AWSHelper:
    """AWS-specific helper for infrastructure and code assistance"""
    
    def __init__(self):
        self.services = {
            'compute': ['EC2', 'Lambda', 'ECS', 'EKS', 'Batch'],
            'storage': ['S3', 'EBS', 'EFS', 'FSx'],
            'database': ['RDS', 'DynamoDB', 'ElastiCache', 'DocumentDB'],
            'networking': ['VPC', 'CloudFront', 'Route53', 'ALB', 'NLB'],
            'security': ['IAM', 'Cognito', 'Secrets Manager', 'KMS'],
            'monitoring': ['CloudWatch', 'X-Ray', 'CloudTrail']
        }
    
    def generate_terraform_ec2(self, config: Dict[str, Any]) -> str:
        """Generate Terraform configuration for EC2 instance"""
        template = '''
# AWS EC2 Instance Configuration
resource "aws_instance" "{name}" {{
  ami           = "{ami}"
  instance_type = "{instance_type}"
  key_name      = "{key_name}"
  
  vpc_security_group_ids = [aws_security_group.{name}_sg.id]
  subnet_id              = "{subnet_id}"
  
  tags = {{
    Name        = "{display_name}"
    Environment = "{environment}"
  }}
  
  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    {user_data}
  EOF
}}

# Security Group for EC2
resource "aws_security_group" "{name}_sg" {{
  name        = "{name}-sg"
  description = "Security group for {display_name}"
  vpc_id      = "{vpc_id}"
  
  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  ingress {{
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["{ssh_cidr}"]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  tags = {{
    Name = "{name}-sg"
  }}
}}
        '''
        return template.format(
            name=config.get('name', 'web_server'),
            ami=config.get('ami', 'ami-0c55b159cbfafe1d0'),
            instance_type=config.get('instance_type', 't2.micro'),
            key_name=config.get('key_name', 'my-key-pair'),
            subnet_id=config.get('subnet_id', 'subnet-12345678'),
            display_name=config.get('display_name', 'Web Server'),
            environment=config.get('environment', 'production'),
            user_data=config.get('user_data', '# Add your startup scripts here'),
            vpc_id=config.get('vpc_id', 'vpc-12345678'),
            ssh_cidr=config.get('ssh_cidr', '10.0.0.0/8')
        ).strip()
    
    def generate_cloudformation_vpc(self, config: Dict[str, Any]) -> str:
        """Generate CloudFormation template for VPC"""
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"VPC with public and private subnets - {config.get('name', 'MyVPC')}",
            "Parameters": {
                "VpcCidr": {
                    "Type": "String",
                    "Default": config.get('vpc_cidr', '10.0.0.0/16'),
                    "Description": "CIDR block for VPC"
                }
            },
            "Resources": {
                "VPC": {
                    "Type": "AWS::EC2::VPC",
                    "Properties": {
                        "CidrBlock": {"Ref": "VpcCidr"},
                        "EnableDnsHostnames": True,
                        "EnableDnsSupport": True,
                        "Tags": [
                            {"Key": "Name", "Value": config.get('name', 'MyVPC')}
                        ]
                    }
                },
                "InternetGateway": {
                    "Type": "AWS::EC2::InternetGateway",
                    "Properties": {
                        "Tags": [
                            {"Key": "Name", "Value": f"{config.get('name', 'MyVPC')}-IGW"}
                        ]
                    }
                },
                "AttachGateway": {
                    "Type": "AWS::EC2::VPCGatewayAttachment",
                    "Properties": {
                        "VpcId": {"Ref": "VPC"},
                        "InternetGatewayId": {"Ref": "InternetGateway"}
                    }
                },
                "PublicSubnet": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "VpcId": {"Ref": "VPC"},
                        "CidrBlock": config.get('public_subnet_cidr', '10.0.1.0/24'),
                        "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
                        "MapPublicIpOnLaunch": True,
                        "Tags": [
                            {"Key": "Name", "Value": f"{config.get('name', 'MyVPC')}-Public-Subnet"}
                        ]
                    }
                },
                "PrivateSubnet": {
                    "Type": "AWS::EC2::Subnet",
                    "Properties": {
                        "VpcId": {"Ref": "VPC"},
                        "CidrBlock": config.get('private_subnet_cidr', '10.0.2.0/24'),
                        "AvailabilityZone": {"Fn::Select": [1, {"Fn::GetAZs": ""}]},
                        "Tags": [
                            {"Key": "Name", "Value": f"{config.get('name', 'MyVPC')}-Private-Subnet"}
                        ]
                    }
                }
            },
            "Outputs": {
                "VPCId": {
                    "Description": "VPC ID",
                    "Value": {"Ref": "VPC"},
                    "Export": {"Name": f"{config.get('name', 'MyVPC')}-VPC-ID"}
                },
                "PublicSubnetId": {
                    "Description": "Public Subnet ID", 
                    "Value": {"Ref": "PublicSubnet"},
                    "Export": {"Name": f"{config.get('name', 'MyVPC')}-Public-Subnet-ID"}
                }
            }
        }
        return json.dumps(template, indent=2)
    
    def generate_lambda_function(self, config: Dict[str, Any]) -> str:
        """Generate AWS Lambda function code"""
        runtime = config.get('runtime', 'python3.9')
        
        if runtime.startswith('python'):
            return '''
import json
import boto3
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda function: {description}
    """
    
    # Initialize AWS clients if needed
    # s3_client = boto3.client('s3')
    # dynamodb = boto3.resource('dynamodb')
    
    try:
        # Your business logic here
        print("Event received: " + json.dumps(event))
        
        response_body = {
            "message": "Function executed successfully",
            "input": event
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response_body)
        }
        
    except Exception as e:
        print("Error: " + str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": str(e)})
        }
            '''.format(description=config.get('description', 'Generated Lambda function'))
        
        elif runtime.startswith('node'):
            return '''
const AWS = require('aws-sdk');

exports.handler = async (event, context) => {
    console.log('Event received:', JSON.stringify(event));
    
    try {
        // Initialize AWS services if needed
        // const s3 = new AWS.S3();
        // const dynamodb = new AWS.DynamoDB.DocumentClient();
        
        // Your business logic here
        
        const response = {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                message: 'Function executed successfully',
                input: event
            })
        };
        
        return response;
        
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ error: error.message })
        };
    }
};
            '''
    
    def get_service_recommendations(self, use_case: str) -> List[str]:
        """Get AWS service recommendations based on use case"""
        recommendations = {
            'web_application': [
                'Use EC2 or ECS for compute',
                'Use ALB for load balancing', 
                'Use RDS for relational database',
                'Use S3 for static assets',
                'Use CloudFront for CDN'
            ],
            'api_backend': [
                'Use Lambda for serverless functions',
                'Use API Gateway for REST APIs',
                'Use DynamoDB for NoSQL database',
                'Use Cognito for authentication',
                'Use CloudWatch for monitoring'
            ],
            'data_processing': [
                'Use EMR for big data processing',
                'Use Glue for ETL jobs',
                'Use Kinesis for streaming data',
                'Use S3 for data lake storage',
                'Use Athena for analytics'
            ],
            'machine_learning': [
                'Use SageMaker for ML workflows',
                'Use S3 for training data storage',
                'Use Lambda for inference endpoints',
                'Use Batch for training jobs',
                'Use CloudWatch for model monitoring'
            ]
        }
        
        return recommendations.get(use_case, [
            'Define your requirements more specifically',
            'Consider AWS Well-Architected Framework principles',
            'Start with basic services and expand as needed'
        ])
    
    def generate_boto3_example(self, service: str, operation: str) -> str:
        """Generate boto3 code examples"""
        examples = {
            'ec2': {
                'list_instances': '''
import boto3

ec2 = boto3.client('ec2')
response = ec2.describe_instances()

for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        print(f"Instance ID: {instance['InstanceId']}")
        print(f"State: {instance['State']['Name']}")
        print(f"Type: {instance['InstanceType']}")
        print("---")
                ''',
                'create_instance': '''
import boto3

ec2 = boto3.client('ec2')

response = ec2.run_instances(
    ImageId='ami-0c55b159cbfafe1d0',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName='my-key-pair',
    SecurityGroupIds=['sg-12345678'],
    SubnetId='subnet-12345678',
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'MyInstance'}
            ]
        }
    ]
)

print(f"Instance created: {response['Instances'][0]['InstanceId']}")
                '''
            },
            's3': {
                'upload_file': '''
import boto3

s3 = boto3.client('s3')

# Upload a file
s3.upload_file('local_file.txt', 'my-bucket', 'remote_file.txt')

# Upload with metadata
s3.upload_file(
    'local_file.txt', 
    'my-bucket', 
    'remote_file.txt',
    ExtraArgs={'Metadata': {'uploaded-by': 'python-script'}}
)
                ''',
                'list_objects': '''
import boto3

s3 = boto3.client('s3')

response = s3.list_objects_v2(Bucket='my-bucket')

for obj in response.get('Contents', []):
    print(f"Key: {obj['Key']}")
    print(f"Size: {obj['Size']} bytes")
    print(f"Modified: {obj['LastModified']}")
    print("---")
                '''
            }
        }
        
        return examples.get(service, {}).get(operation, f"# Example for {service} {operation} not available")


# Example usage
if __name__ == "__main__":
    aws_helper = AWSHelper()
    
    # Generate EC2 Terraform
    ec2_config = {
        'name': 'web_server',
        'ami': 'ami-0abcdef1234567890',
        'instance_type': 't3.micro',
        'environment': 'development'
    }
    
    print("EC2 Terraform Configuration:")
    print(aws_helper.generate_terraform_ec2(ec2_config))
    
    print("\n" + "="*50 + "\n")
    
    # Get recommendations
    print("Web Application Recommendations:")
    for rec in aws_helper.get_service_recommendations('web_application'):
        print(f"- {rec}")