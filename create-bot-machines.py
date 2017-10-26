#!/usr/bin/env python3
import argparse
import sys

import boto3
import time


def create_machines(args):
    tags = [{
            "ResourceType": "instance",
            "Tags": [{
                "Key": "Bot",
                "Value": args.tag
            }]}]

    ec2 = boto3.client("ec2")
    response = ec2.run_instances(
        ImageId=args.image,
        InstanceType=args.size,
        KeyName=args.key,
        SecurityGroups=[args.security_group],
        TagSpecifications=tags,
        MinCount=args.count,
        MaxCount=args.count
    )

    instances = response["Instances"]
    instance_ids = [i["InstanceId"] for i in instances]
    print("Created %d instances" % len(instance_ids))
    for i, instance in enumerate(instances):
        instance_id = instance["InstanceId"]
        print(instance_id)
        tag = "%s-%d" % (args.tag, i + 1)
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[
                {"Key": "Name", "Value": tag}
            ]
        )

    if args.wait:
        wait_for_instances(instance_ids)


def wait_for_instances(instance_ids):
    instances_remaining = instance_ids
    while instances_remaining:
        running_instances = get_running_instances(instance_ids)

        instances_remaining = []
        for each in instance_ids:
            if each not in running_instances:
                instances_remaining.append(each)

        if instances_remaining:
            print("%d machines still pending" % len(instances_remaining))
            time.sleep(5)


def get_running_instances(instance_ids):
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances(
        InstanceIds=instance_ids,
        Filters=[
            {
                "Name": "instance-state-name",
                "Values": ["running"]
            }
        ]
    )
    running_instances = []
    reservations = response["Reservations"]
    for groups in reservations:
        instances = groups["Instances"]
        for instance in instances:
            running_instances.append(instance["InstanceId"])
    return running_instances


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--image",
        default="ami-785db401",
        help="The machine image (AMI) to use"
    )
    parser.add_argument(
        "-k", "--key",
        required=True,
        help="The name of a key file (.pem)"
    )
    parser.add_argument(
        "-s", "--size",
        default="t2.micro",
        help="The machine size"
    )
    parser.add_argument(
        "-c", "--security-group",
        required=True,
        help="The security group"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=1,
        help="The number of machines to create"
    )
    parser.add_argument(
        "-t", "--tag",
        default="run-bot",
        help="The base name for a Name tag"
    )
    parser.add_argument(
        "-w", "--wait",
        action="store_true",
        help="Wait until all instances are in the running state"
    )

    args = parser.parse_args()
    
    create_machines(args)

if __name__ == "__main__":
    sys.exit(main())