import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError


def load_env_file(path=".env"):
    """Manually load environment variables from a .env file."""
    if not os.path.exists(path):
        print(f"⚠️ .env file not found at: {path}")
        return

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
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


def test_aws_connection():
    """Test AWS connection for multiple accounts and regions"""
    load_env_file()

    account_ids_str = os.getenv("ACCOUNT_IDS", "")

    account_ids = [
        x.strip() for x in account_ids_str.split(",") if x.strip()
    ]

    regions = get_available_regions()
    print(f"🌍 Testing across {len(regions)} AWS regions...")

    for account_suffix in account_ids:
        print(f"\n🔹 Testing AWS account [{account_suffix}]...")

        access_key_id = "aws_access_key_id_" + account_suffix
        secret_access_key = "aws_secret_access_key_" + account_suffix
        session_token = "aws_session_token_" + account_suffix

        aws_access_key = os.getenv(access_key_id)
        aws_secret_key = os.getenv(secret_access_key)
        aws_token = os.getenv(session_token)

        if not aws_access_key or not aws_secret_key:
            print("❌ Error: Missing AWS credentials!")
            continue

        account_accessible_regions = []
        
        for region in regions:
            try:
                sts = boto3.client(
                    "sts",
                    region_name=region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    aws_session_token=aws_token,
                )

                identity = sts.get_caller_identity()
                account_accessible_regions.append(region)
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code in ['UnauthorizedOperation', 'AccessDenied']:
                    print(f"   ⚠️ [{region}]: Access denied")
                elif error_code == 'OptInRequired':
                    print(f"   ⚠️ [{region}]: Opt-in required")
                else:
                    print(f"   ⚠️ [{region}]: {e.response['Error']['Message']}")
                continue
            except EndpointConnectionError:
                print(f"   ⚠️ [{region}]: Could not connect to endpoint")
                continue
            except Exception as e:
                print(f"   ⚠️ [{region}]: {str(e)}")
                continue

        if account_accessible_regions:
            print("✅ AWS connection successful!")
            print("   Account ID:", identity["Account"])
            print("   User ARN:", identity["Arn"])
            print("   User ID:", identity.get("UserId", "N/A"))
            print(f"   🌍 Accessible regions: {len(account_accessible_regions)}/{len(regions)}")
            if len(account_accessible_regions) <= 10:
                print(f"   📍 Regions: {', '.join(account_accessible_regions)}")
            else:
                print(f"   📍 First 10 regions: {', '.join(account_accessible_regions[:10])}...")
        else:
            print("❌ No accessible regions found for this account!")


if __name__ == "__main__":
    test_aws_connection()
