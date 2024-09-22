"""
Note: you must be logged into the AWS CLI to run this script.
"""
import time
import boto3

ec2 = boto3.client('ec2', region_name='us-east-2')  # Replace with your desired region

# Describe VPCs and filter for the default VPC
response = ec2.describe_vpcs(
    Filters=[{'Name': 'isDefault', 'Values': ['true']}]
)
default_vpc = response['Vpcs'][0]['VpcId']
print(f'Default VPC ID: {default_vpc}')

instance_name = input("Enter a name for your EC2 instance: ")

# Step 1: Create a Security Group
response = ec2.create_security_group(
    GroupName=f'{instance_name}SecurityGroup-{int(time.time())}',
    Description='Allow traffic from anywhere',
    VpcId=default_vpc
)
security_group_id = response['GroupId']
print(f'Security Group Created {security_group_id}')

# Step 2: Set Inbound Rules to allow traffic from anywhere (0.0.0.0/0 for IPv4)
ec2.authorize_security_group_ingress(
    GroupId=security_group_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,  # SSH port
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,  # HTTP port
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,  # HTTPS port
            'ToPort': 443,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 8000,   # Custom port for your application, used for backend
            'ToPort': 8000,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 3000,   # Custom port for your application, used for frontend
            'ToPort': 3000,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)

print('Ingress Successfully Set for SSH (22), HTTP (80), and HTTPS (443).')

key_pair_name = input("Enter the AWS key pair name (default: 'AWS Key Par'): ") or "AWS Key Par"

# Step 3: Launch a new EC2 instance with this Security Group and the user-defined name
response = ec2.run_instances(
    ImageId='ami-037774efca2da0726',  # Replace with your AMI ID, currently Amazon Linux 2023 AMI
    InstanceType='t2.micro',          # Replace with your desired instance type
    MinCount=1,
    MaxCount=1,
    KeyName=key_pair_name,          
    SecurityGroupIds=[security_group_id],    # Use the security group created
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': instance_name  # Set the instance name from user input
                }
            ]
        }
    ]

)

instance_id = response['Instances'][0]['InstanceId']
print(f'EC2 Instance {instance_id} launched with name "{instance_name}" and security group {security_group_id}')
