# AWS EC2 Instance Parser

This project is a set of tools for working with AWS EC2 instances, allowing you to collect information about instances from multiple AWS accounts and search through them.

## 📋 Description

The project consists of three main components:

1. **EC2_info_parser.py** - main script for collecting EC2 instance information
2. **test_connection.py** - utility for testing AWS account connections
3. **find.py** - tool for searching specific instances by name

## 🚀 Features

- ✅ Support for multiple AWS accounts
- ✅ Automatic collection of EC2 instance information from all AWS regions
- ✅ **Parallel processing** for maximum performance (4x faster)
- ✅ Data export to JSON format
- ✅ Instance search by name through tags
- ✅ AWS connection testing across all regions
- ✅ Error handling and detailed logging
- ✅ Automatic discovery of available regions
- ✅ **Performance timing** with detailed statistics

## 📦 Installation

### Requirements

- Python 3.6+
- AWS accounts with configured credentials

### Install dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

- `boto3==1.40.53` - AWS SDK for Python
- `botocore==1.40.53` - Core boto3 components
- `python-dotenv==1.1.1` - Working with .env files

## ⚙️ Configuration

### 1. Create configuration file

Copy the `env-exemple` file to `.env` and fill it:

```bash
cp env-exemple .env
```

### 2. Configure AWS credentials

Edit the `.env` file and add credentials for each account:

```env
# Account 1
aws_access_key_id_318=YOUR_ACCESS_KEY_ID_1
aws_secret_access_key_318=YOUR_SECRET_ACCESS_KEY_1
aws_session_token_318=YOUR_SESSION_TOKEN_1

# Account 2
aws_access_key_id_054=YOUR_ACCESS_KEY_ID_2
aws_secret_access_key_054=YOUR_SECRET_ACCESS_KEY_2
aws_session_token_054=YOUR_SESSION_TOKEN_2

# Account 3
aws_access_key_id_144=YOUR_ACCESS_KEY_ID_3
aws_secret_access_key_144=YOUR_SECRET_ACCESS_KEY_3
aws_session_token_144=YOUR_SESSION_TOKEN_3

# List of accounts to process
ACCOUNT_IDS=318,054,144
```

### 3. Getting AWS credentials

To get temporary credentials, use AWS CLI:

```bash
aws sts assume-role --role-arn arn:aws:iam::ACCOUNT-ID:role/ROLE-NAME --role-session-name session-name
```

Or configure AWS CLI profiles:

```bash
aws configure --profile account-318
aws configure --profile account-054
aws configure --profile account-144
```

## 🎯 Usage

### 1. Testing connection

Before using the main functionality, it's recommended to test the connection to AWS accounts:

```bash
python test_connection.py
```

**Expected result:**
```
🌍 Testing across 25 AWS regions...

🔹 Testing AWS account [318]...
   ⚠️ [ap-northeast-3]: Opt-in required
   ⚠️ [ap-southeast-3]: Access denied
✅ AWS connection successful!
   Account ID: 123456789012
   User ARN: arn:aws:sts::123456789012:assumed-role/RoleName/session-name
   User ID: AROAEXAMPLE123456789:session-name
   🌍 Accessible regions: 23/25
   📍 First 10 regions: us-east-1, us-west-2, eu-west-1, eu-central-1...
```

### 2. Collecting instance information

Run the main script to collect information:

```bash
python EC2_info_parser.py
```

**What happens:**
- Credentials are loaded from the `.env` file
- Connects to each specified AWS account
- Collects information about all EC2 instances
- Data is saved to the `instances.json` file

**Example output:**
```
Starting EC2 instance collection at 2025-10-17 04:59:06
Processing 3 accounts in parallel...
Scanning 17 regions for account [318] (parallel)...
Scanning 17 regions for account [144] (parallel)...
Scanning 17 regions for account [054] (parallel)...
   [eu-west-1]: 13 instances
   [eu-central-1]: 169 instances
   [us-east-1]: 1131 instances
   [us-west-2]: 34 instances
Found 1347 total instances in account [318]

Fetching EC2 instances for account [318]...
   [us-east-1]: 1023 instances
Found 1023 total instances in account [054]

Fetching EC2 instances for account [054]...
   [us-east-1]: 955 instances
Found 983 total instances in account [144]

Saved all instance data to 'instances.json' (3353 total instances).
Total execution time: 23.63 seconds (0.39 minutes)
Average time per instance: 7.05 ms
Completed at 2025-10-17 04:59:29
```

### 3. Searching instances

After creating the `instances.json` file, you can search for specific instances:

**Usage from terminal in current directory:**
```bash
py find.py instance-name
# or
python find.py instance-name
```

## 📊 Data Structure

### Data Fields

| Field | Description |
|-------|-------------|
| `Account` | Account suffix (from ACCOUNT_IDS variable) |
| `Region` | AWS region where the instance is located |
| `InstanceId` | Unique EC2 instance identifier |
| `InstanceType` | Instance type (e.g., t3.medium, m5.large) |
| `State` | Current instance state (running, stopped, pending, etc.) |
| `PrivateIpAddress` | Private IP address of the instance |
| `PublicIpAddress` | Public IP address of the instance (if available) |
| `Tags` | Dictionary of all instance tags |

## ⚡ Performance Optimization

The script uses **parallel processing** for maximum performance:

### Parallel Execution Levels

1. **Account Level**: All AWS accounts are processed simultaneously (up to 3 threads)
2. **Region Level**: All regions within each account are scanned in parallel (up to 10 threads)

### Performance Metrics

| Metric | Sequential | Parallel | Improvement |
|--------|------------|----------|-------------|
| **Total Time** | ~102 seconds | **~24 seconds** | **🚀 4.3x faster** |
| **Time per Instance** | ~30 ms | **~7 ms** | **🚀 4.3x faster** |
| **Throughput** | ~33 instances/sec | **~142 instances/sec** | **🚀 4.3x faster** |

### Technical Details

- **ThreadPoolExecutor** manages concurrent execution
- **as_completed()** processes results as they become available
- **Configurable thread limits** prevent AWS API rate limiting
- **Real-time progress** shows completion status

### Performance Timing

The script provides detailed timing information:
- Start and completion timestamps
- Total execution time (seconds and minutes)
- Average processing time per instance
- Real-time progress updates

## 🛠️ Extending Functionality

### Adding new accounts

1. Add credentials to the `.env` file:
```env
aws_access_key_id_NEW=YOUR_ACCESS_KEY
aws_secret_access_key_NEW=YOUR_SECRET_KEY
aws_session_token_NEW=YOUR_SESSION_TOKEN
```

2. Update the account list:
```env
ACCOUNT_IDS=318,054,144,NEW
```

### Adding additional fields

To collect additional instance information, edit the `get_all_instances_for_account()` function:

```python
instance_data = {
    "Account": account_suffix,
    "Region": region,
    "InstanceId": instance["InstanceId"],
    "InstanceType": instance.get("InstanceType", "N/A"),
    "State": instance["State"]["Name"],
    "PrivateIpAddress": instance.get("PrivateIpAddress", "N/A"),
    "PublicIpAddress": instance.get("PublicIpAddress", "N/A"),
    "LaunchTime": instance.get("LaunchTime", "N/A"),  
    "VpcId": instance.get("VpcId", "N/A"),           
    "SubnetId": instance.get("SubnetId", "N/A"),
    "Tags": tags,
}
```

## 🚨 Error Handling

The script includes handling for the following error types:

- **NoCredentialsError** - missing credentials
- **ClientError** - AWS API errors
- **EndpointConnectionError** - AWS connection issues
- **General exceptions** - unexpected errors

## 📝 Logging

All operations are logged using emojis for easy reading:

- 🔹 Informational messages
- ✅ Successful operations
- ❌ Errors
- ⚠️ Warnings

## 🔒 Security

⚠️ **Important security recommendations:**

1. **Never commit the `.env` file** to version control
2. Use temporary credentials (session tokens)
3. Limit credential access rights to only necessary resources
4. Regularly rotate credentials
5. Use IAM roles instead of long-term access keys

## 📋 Required Access Rights

Minimum IAM rights required for script operation:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeRegions",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🐛 Troubleshooting

### Problem: "Credentials missing"

**Solution:**
1. Check the correctness of the `.env` file
2. Ensure environment variables are loaded correctly
3. Check that the session token hasn't expired

### Problem: "Could not connect to AWS endpoint"

**Solution:**
1. Check internet connection
2. Ensure there's no firewall blocking
3. Check the correct region

### Problem: "No instances found"

**Solution:**
1. Ensure there are EC2 instances in the account
2. Check EC2 access rights
3. Check the correct region

## 📄 License

This project is distributed freely for internal use.

## 🤝 Support

When encountering problems:

1. Check execution logs
2. Ensure correct credential configuration
3. Check AWS resource access rights
4. Refer to AWS documentation for additional information