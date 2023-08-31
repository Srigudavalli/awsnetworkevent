import boto3
import json
from decimal import Decimal
from botocore.exceptions import ClientError

def dynamodb_insert_data(table_name, item):
  
  dynamodb = boto3.resource('dynamodb')
  
  table = dynamodb.Table(table_name)
  table.put_item(Item=item)
  print(f"Inserted {len(item)} items into table {table_name}")

def lambda_handler(event, context):
    # Create an EC2 client
    ec2_client = boto3.client('ec2')
    table_name = "ipam_aws"

    # 2: Get the list of AWS IPAM scopes
    ipam_scope = ec2_client.describe_ipam_scopes()
    print(ipam_scope)
    
    for scope in ipam_scope['IpamScopes']:
        print(scope)
        ipamscopeid= scope['IpamScopeId']
        ipam_discoverd = ec2_client.get_ipam_resource_cidrs(IpamScopeId=ipamscopeid)
        print(ipam_discoverd)
        for ipamresourcecidr in ipam_discoverd['IpamResourceCidrs']:
            print (ipamresourcecidr)
            print (ipamresourcecidr['ResourceId'])
            if ipamresourcecidr['ResourceType'] != 'eip':  
              record={
                'ResourceId' : ipamresourcecidr['ResourceId'],
                'ResourceOwnerId': ipamresourcecidr['ResourceOwnerId'],
                'ResourceRegion' : ipamresourcecidr['ResourceRegion'],
                'ResourceType' : ipamresourcecidr['ResourceType'],
                'ResourceCidr' : ipamresourcecidr['ResourceCidr'],
                'IpUsage' : ipamresourcecidr['IpUsage'],
                'VpcId' : ipamresourcecidr['VpcId'],
                }
              item = json.loads(json.dumps(record), parse_float=Decimal)
              print(item)
            else:
              record={
                'ResourceId' : ipamresourcecidr['ResourceId'],
                'ResourceOwnerId': ipamresourcecidr['ResourceOwnerId'],
                'ResourceRegion' : ipamresourcecidr['ResourceRegion'],
                'ResourceType' : ipamresourcecidr['ResourceType'],
                'ResourceCidr' : ipamresourcecidr['ResourceCidr'],
                'IpUsage' : "100",
                'VpcId' : 'none',
                }
              item = json.loads(json.dumps(record), parse_float=Decimal)
              print(item)
            dynamodb_insert_data(table_name, item)
           
           
    return {
        'statusCode': 200,
        'body': 'Process completed'
    }