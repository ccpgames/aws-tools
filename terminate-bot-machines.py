import argparse
import sys

import boto3


def terminate_machines(args):
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "tag:Bot",
                "Values": [args.tag]
            },
            {
                "Name": "instance-state-name",
                "Values": ["running", "stopped"]
            }
        ]
    )

    instance_ids = []
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
            instance_id = instance["InstanceId"]
            print(instance_id, name, state)
            instance_ids.append(instance_id)

    if not instance_ids:
        print("No machines found")
        return

    if not args.confirm:
        confirm = input("Are you sure you want to terminate these machines? (y/n) ")
        if not confirm.lower() == "y":
            return

    ec2.terminate_instances(
        InstanceIds=instance_ids
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t", "--tag",
        default="run-bot",
        help="The base name for a Name tag"
    )

    parser.add_argument(
        "-y", "--confirm",
        action="store_true",
        help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    terminate_machines(args)


if __name__ == "__main__":
    sys.exit(main())