import boto3
import os
import json
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


def get_all_instances_for_account(account_suffix, region="us-east-1"):
    """Fetch all EC2 instances and their tags for one account."""
    try:
        access_key_id = f"aws_access_key_id_{account_suffix}"
        secret_access_key = f"aws_secret_access_key_{account_suffix}"
        session_token = f"aws_session_token_{account_suffix}"

        ec2 = boto3.client(
            "ec2",
            region_name=region,
            aws_access_key_id=os.getenv(access_key_id),
            aws_secret_access_key=os.getenv(secret_access_key),
            aws_session_token=os.getenv(session_token),
        )

        response = ec2.describe_instances()
        instances = []

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                instance_data = {
                    "Account": account_suffix,
                    "InstanceId": instance["InstanceId"],
                    "InstanceType": instance.get("InstanceType", "N/A"),
                    "State": instance["State"]["Name"],
                    "PrivateIpAddress": instance.get("PrivateIpAddress", "N/A"),
                    "PublicIpAddress": instance.get("PublicIpAddress", "N/A"),
                    "Tags": tags,
                }
                instances.append(instance_data)

        print(f"✅ Found {len(instances)} instances in account [{account_suffix}]")
        return instances

    except ClientError as e:
        print(f"❌ AWS client error in account [{account_suffix}]: {e.response['Error']['Message']}")
    except NoCredentialsError:
        print(f"❌ Credentials missing for account [{account_suffix}]")
    except EndpointConnectionError:
        print(f"❌ Could not connect to AWS endpoint for account [{account_suffix}]")
    except Exception as e:
        print(f"❌ Unexpected error in account [{account_suffix}]: {e}")

    return []


def collect_all_instances():
    """Collect EC2 instances from all accounts and save them to a JSON file."""
    load_env_file()

    account_ids_str = os.getenv("ACCOUNT_IDS", "")

    account_ids = [
        x.strip() for x in account_ids_str.split(",") if x.strip()
    ]

    all_instances = []

    for account_suffix in account_ids:
        print(f"\n🔹 Fetching EC2 instances for account [{account_suffix}]...")
        instances = get_all_instances_for_account(account_suffix)
        all_instances.extend(instances)

    output_file = "instances.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_instances, f, indent=4, ensure_ascii=False)

    print(f"\n💾 Saved all instance data to '{output_file}' ({len(all_instances)} total instances).")


if __name__ == "__main__":
    collect_all_instances()
