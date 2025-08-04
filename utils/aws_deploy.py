import boto3
import paramiko
import time
import os

def get_latest_ubuntu_ami(ec2_client):
    response = ec2_client.describe_images(
        Owners=["099720109477"],  # Canonical
        Filters=[
            {"Name": "name", "Values": ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]},
            {"Name": "state", "Values": ["available"]}
        ]
    )
    images = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)
    return images[0]["ImageId"]

def run_ssh_command(ssh, command):
    print(f"[SSH] ➤ {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"[STDOUT]\n{out}")
    if err:
        print(f"[STDERR]\n{err}")
    return out, err

def deploy_to_aws_ec2(aws_access_key, aws_secret_key, region, repo_path, tech_stack) -> str:
    print("\n[STEP 1] 🔍 Determining application port based on tech stack...")
    port_map = {"nodejs": "3000", "flask": "5000", "springboot": "8080"}
    app_port = port_map.get(tech_stack, "3000")
    print(f"[INFO] ➤ Tech stack: {tech_stack}, exposing port: {app_port}")

    ec2 = boto3.resource("ec2", region_name=region,
                         aws_access_key_id=aws_access_key,
                         aws_secret_access_key=aws_secret_key)
    ec2_client = boto3.client("ec2", region_name=region,
                              aws_access_key_id=aws_access_key,
                              aws_secret_access_key=aws_secret_key)

    print("\n[STEP 2] 🧠 Fetching latest Ubuntu AMI ID...")
    ami_id = get_latest_ubuntu_ami(ec2_client)
    print(f"[INFO] ✅ Using AMI ID: {ami_id}")

    key_name = "autodock-key"
    key_path = os.path.expanduser("~/.ssh/autodock-key.pem")

    if not os.path.exists(key_path):
        print("\n[STEP 3] 🔐 Creating EC2 Key Pair...")
        key_pair = ec2_client.create_key_pair(KeyName=key_name)
        with open(key_path, "w") as key_file:
            key_file.write(key_pair["KeyMaterial"])
        os.chmod(key_path, 0o400)
        print(f"[INFO] ✅ Key saved to: {key_path}")
    else:
        print(f"[INFO] ✅ Key already exists at: {key_path}")

    print("\n[STEP 4] 🔒 Creating or reusing security group...")
    vpc_id = ec2_client.describe_vpcs()["Vpcs"][0]["VpcId"]
    sg_id = create_security_group(ec2_client, vpc_id, group_name="autodock-sg")
    print(f"[INFO] ✅ Using Security Group ID: {sg_id}")

    print("\n[STEP 5] 🚀 Launching EC2 instance...")
    try:
        instance = ec2.create_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            KeyName=key_name,
            SecurityGroupIds=[sg_id]
        )[0]
    except Exception as e:
        raise RuntimeError(f"[ERROR] ❌ Failed to launch EC2 instance: {e}")

    print("[INFO] ⏳ Waiting for EC2 instance to boot...")
    instance.wait_until_running()
    instance.load()
    public_ip = instance.public_ip_address
    print(f"[SUCCESS] ✅ EC2 is running at: {public_ip}")

    print("\n[STEP 6] ⏳ Waiting 60s for EC2 to finish booting...")
    time.sleep(90)

    print("\n[STEP 7] 🔌 Connecting to EC2 via SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    k = paramiko.RSAKey.from_private_key_file(key_path)

    try:
        ssh.connect(hostname=public_ip, username="ubuntu", pkey=k)
        print("[SUCCESS] ✅ SSH connection established.")
    except Exception as e:
        raise RuntimeError(f"[ERROR] ❌ SSH failed: {e}")

    print("\n[STEP 8] ⚙️ Running provisioning commands on EC2...")
    run_ssh_command(ssh, "sudo apt update -y")
    run_ssh_command(ssh, "sudo apt install -y docker.io git")

    # Clean repo URL and folder name
    repo_path = repo_path.strip()
    repo_folder_name = repo_path.rstrip("/").split("/")[-1].replace(".git", "")

    print(f"\n[STEP 9] 📥 Cloning repo: {repo_path}")
    run_ssh_command(ssh, f"git clone {repo_path}")

    print(f"\n[STEP 10] 🐳 Building Docker image for: {repo_folder_name}")
    run_ssh_command(ssh, f"cd {repo_folder_name} && sudo docker build -t app .")

    print(f"\n[STEP 11] 🏃 Running Docker container on port 80 → {app_port}")
    run_ssh_command(ssh, f"sudo docker run -d -p 80:{app_port} app")

    ssh.close()
    print("\n[FINAL] 🎉 Deployment complete!")
    print(f"[ACCESS] ➜ http://{public_ip}")
    return public_ip

def ensure_ssh_rule(ec2_client, security_group_id):
    try:
        response = ec2_client.describe_security_groups(GroupIds=[security_group_id])
        permissions = response['SecurityGroups'][0]['IpPermissions']

        ssh_rule_exists = any(
            perm['IpProtocol'] == 'tcp' and
            perm.get('FromPort') == 22 and
            perm.get('ToPort') == 22
            for perm in permissions
        )

        if ssh_rule_exists:
            print("[INFO] ✅ SSH rule already exists in Security Group.")
            return

        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[{
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            }]
        )
        print("[INFO] ✅ SSH rule added to Security Group.")
    except Exception as e:
        print(f"[ERROR] ❌ Failed to validate SSH rule: {e}")

def create_or_get_security_group(ec2_client, group_name, description, port):
    vpc_id = ec2_client.describe_vpcs()["Vpcs"][0]["VpcId"]
    try:
        groups = ec2_client.describe_security_groups(Filters=[
            {'Name': 'group-name', 'Values': [group_name]}
        ])
        if groups["SecurityGroups"]:
            sg_id = groups["SecurityGroups"][0]["GroupId"]
            print(f"[INFO] ➤ Security group '{group_name}' already exists. Reusing SG.")
            return sg_id

        sg = ec2_client.create_security_group(
            GroupName=group_name,
            Description=description,
            VpcId=vpc_id
        )
        sg_id = sg["GroupId"]

        # Add inbound rules
        ingress_rules = [
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': port, 'ToPort': port,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        ]

        ec2_client.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=ingress_rules
        )
        print(f"[INFO] ➤ Created SG '{group_name}' with rules.")
        return sg_id

    except ec2_client.exceptions.ClientError as e:
        if "InvalidPermission.Duplicate" in str(e):
            print("[WARN] Some rules already exist. Continuing.")
            return sg_id
        raise RuntimeError(f"[ERROR] ❌ SG creation failed: {e}")

def create_security_group(ec2_client, vpc_id, group_name="autodock-sg") -> str:
    import time
    try:
        response = ec2_client.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [group_name]}]
        )
        if response["SecurityGroups"]:
            return response["SecurityGroups"][0]["GroupId"]
    except ec2_client.exceptions.ClientError:
        pass

    sg = ec2_client.create_security_group(
        GroupName=group_name,
        Description="Security group for AutoDock EC2",
        VpcId=vpc_id,
    )
    sg_id = sg["GroupId"]
    time.sleep(1)

    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 80,
                "ToPort": 80,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
        ],
    )

    print(f"[✓] Created Security Group: {sg_id}")
    return sg_id


