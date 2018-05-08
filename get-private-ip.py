#!/usr/bin/env python3
import argparse
import sys

import boto3


def get_private_ip(name):
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "tag:Name",
                "Values": [name]
            }
        ]
    )
    reservations = response["Reservations"]
    for groups in reservations:
        instances = groups["Instances"]
        for instance in instances:
            tags = instance["Tags"]
            name = ""
            for tag in tags:
                if tag["Key"] == "Name":
                    name = tag["Value"]
                    break
            state = instance["State"]["Name"]
            print(instance["PrivateIpAddress"])


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "name",
        help="The name of the machine"
    )

    args = parser.parse_args()

    get_private_ip(args.name)

if __name__ == "__main__":
    sys.exit(main())