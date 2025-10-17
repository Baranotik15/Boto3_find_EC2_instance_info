import boto3
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


def load_env_file(path=".env"):
    """Manually load environment variables from a .env file."""
    if not os.path.exists(path):
        print(f"⚠️ .env file not found at: {path}")
        return

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()


def get_available_regions():
    """Get list of all available AWS regions."""
    try:
        ec2 = boto3.client("ec2", region_name="us-east-1")
        response = ec2.describe_regions()
        return [region["RegionName"] for region in response["Regions"]]
    except Exception as e:
        print(f"⚠️ Could not fetch regions, using default: {e}")
        return ["us-east-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1"]


def get_instances_for_account_region(account_suffix, region, aws_access_key, aws_secret_key, aws_token):
    """Fetch EC2 instances for one account in one specific region."""
    try:
        ec2 = boto3.client(
            "ec2",
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_token,
        )

        response = ec2.describe_instances()
        region_instances = []

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                instance_data = {
                    "Account": account_suffix,
                    "Region": region,
                    "InstanceId": instance["InstanceId"],
                    "InstanceType": instance.get("InstanceType", "N/A"),
                    "State": instance["State"]["Name"],
                    "PrivateIpAddress": instance.get("PrivateIpAddress", "N/A"),
                    "PublicIpAddress": instance.get("PublicIpAddress", "N/A"),
                    "Tags": tags,
                }
                region_instances.append(instance_data)

        return region, len(region_instances), region_instances

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ['UnauthorizedOperation', 'AccessDenied']:
            return region, 0, f"Access denied"
        elif error_code == 'OptInRequired':
            return region, 0, f"Opt-in required"
        else:
            return region, 0, f"{e.response['Error']['Message']}"
    except EndpointConnectionError:
        return region, 0, f"Could not connect to endpoint"
    except Exception as e:
        return region, 0, f"{str(e)}"


def get_all_instances_for_account(account_suffix):
    """Fetch all EC2 instances and their tags for one account from all regions."""
    access_key_id = f"aws_access_key_id_{account_suffix}"
    secret_access_key = f"aws_secret_access_key_{account_suffix}"
    session_token = f"aws_session_token_{account_suffix}"
    
    aws_access_key = os.getenv(access_key_id)
    aws_secret_key = os.getenv(secret_access_key)
    aws_token = os.getenv(session_token)
    
    if not aws_access_key or not aws_secret_key:
        print(f"Credentials missing for account [{account_suffix}]")
        return []
    
    try:
        regions = get_available_regions()
        print(f"Scanning {len(regions)} regions for account [{account_suffix}] (parallel)...")
        
        all_instances = []
        
        # Use ThreadPoolExecutor for parallel region scanning
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all region tasks
            future_to_region = {
                executor.submit(
                    get_instances_for_account_region, 
                    account_suffix, 
                    region, 
                    aws_access_key, 
                    aws_secret_key, 
                    aws_token
                ): region for region in regions
            }
            
            # Process completed tasks
            for future in as_completed(future_to_region):
                region = future_to_region[future]
                try:
                    region_name, count, result = future.result()
                    
                    if isinstance(result, list):
                        # Success - we got instances
                        if count > 0:
                            print(f"   [{region_name}]: {count} instances")
                            all_instances.extend(result)
                    else:
                        # Error message
                        print(f"   [{region_name}]: {result}")
                        
                except Exception as e:
                    print(f"   [{region}]: Unexpected error: {e}")

        print(f"Found {len(all_instances)} total instances in account [{account_suffix}]")
        return all_instances

    except NoCredentialsError:
        print(f"Credentials missing for account [{account_suffix}]")
    except Exception as e:
        print(f"Unexpected error in account [{account_suffix}]: {e}")

    return []


def collect_all_instances():
    """Collect EC2 instances from all accounts and save them to a JSON file."""
    start_time = time.time()
    print(f"Starting EC2 instance collection at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    load_env_file()

    account_ids_str = os.getenv("ACCOUNT_IDS", "")

    account_ids = [
        x.strip() for x in account_ids_str.split(",") if x.strip()
    ]

    all_instances = []

    # Use ThreadPoolExecutor for parallel account processing
    print(f"Processing {len(account_ids)} accounts in parallel...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all account tasks
        future_to_account = {
            executor.submit(get_all_instances_for_account, account_suffix): account_suffix 
            for account_suffix in account_ids
        }
        
        # Process completed tasks
        for future in as_completed(future_to_account):
            account_suffix = future_to_account[future]
            try:
                print(f"\nFetching EC2 instances for account [{account_suffix}]...")
                instances = future.result()
                all_instances.extend(instances)
            except Exception as e:
                print(f"Error processing account [{account_suffix}]: {e}")

    output_file = "instances.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_instances, f, indent=4, ensure_ascii=False)

    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\nSaved all instance data to '{output_file}' ({len(all_instances)} total instances).")
    print(f"Total execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")
    print(f"Average time per instance: {execution_time/len(all_instances)*1000:.2f} ms")
    print(f"Completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    collect_all_instances()
