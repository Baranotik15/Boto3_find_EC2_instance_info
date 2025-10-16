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


def test_aws_connection():
    """Test AWS connection for multiple accounts"""
    load_env_file()

    account_ids_str = os.getenv("ACCOUNT_IDS", "")

    account_ids = [
        x.strip() for x in account_ids_str.split(",") if x.strip()
    ]

    for account_suffix in account_ids:
        print(f"\n🔹 Testing AWS account [{account_suffix}]...")

        try:
            access_key_id = "aws_access_key_id_" + account_suffix
            secret_access_key = "aws_secret_access_key_" + account_suffix
            session_token = "aws_session_token_" + account_suffix

            sts = boto3.client(
                "sts",
                region_name="us-east-1",
                aws_access_key_id=os.getenv(access_key_id),
                aws_secret_access_key=os.getenv(secret_access_key),
                aws_session_token=os.getenv(session_token),
            )

            identity = sts.get_caller_identity()

            print("✅ AWS connection successful!")
            print("   Account ID:", identity["Account"])
            print("   User ARN:", identity["Arn"])
            print("   User ID:", identity.get("UserId", "N/A"))

        except NoCredentialsError:
            print("❌ Error: Missing or invalid AWS credentials!")

        except ClientError as e:
            print(f"❌ AWS client error: {e.response['Error']['Message']}")

        except EndpointConnectionError:
            print("❌ Network error: Could not connect to AWS endpoint.")

        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    test_aws_connection()
