import argparse
import sys

import boto3


def list_machines(args):
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "tag:Bot",
                "Values": [args.tag]
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
            print(instance["InstanceId"], name, state)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t", "--tag",
        default="run-bot",
        help="The base name for a Name tag"
    )

    args = parser.parse_args()

    list_machines(args)


if __name__ == "__main__":
    sys.exit(main())