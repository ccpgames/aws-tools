#!/usr/bin/env python3
import argparse
import sys

import boto3
import botocore
import time


ec2 = boto3.client("ec2")


def create_image(args):
    instance_ids = get_machine_instances(args)

    if not instance_ids:
        print("No machines found")
        return 1

    instance = instance_ids[0]
    print("Creating an image from %s" % instance)

    if not args.confirm:
        confirm = input("Continue? (y/n) ")
        if not confirm.lower() == "y":
            return 2

    ec2 = boto3.client("ec2")
    try:
        response = ec2.create_image(
            InstanceId=instance,
            Name=args.name
        )
    except botocore.exceptions.ClientError as e:
        print(e)
        return 3

    image_id = response["ImageId"]
    print("Creating image %s" % image_id)

    if args.wait:
        result = wait_for_image(image_id)
        if result != "available":
            return 4

    return 0


def get_machine_instances(args):
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
    reservations = response["Reservations"]
    instance_ids = []
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
            instance_ids.append(instance["InstanceId"])

    return instance_ids


def wait_for_image(image_id):
    while True:
        response = ec2.describe_images(
            Filters=[
                {
                    "Name": "image-id",
                    "Values": [image_id]
                }
            ]
        )

        images = response["Images"]
        if not images:
            return "error"

        image = images[0]
        if image["State"] != "pending":
            return image["State"]

        time.sleep(30)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t", "--tag",
        default="run-bot",
        help="The name tag of a machine to use as the basis for the image"
    )

    parser.add_argument(
        "-n", "--name",
        default="run-bot-image",
        help="The name to use for the resulting image"
    )

    parser.add_argument(
        "-y", "--confirm",
        action="store_true",
        help="Skip confirmation prompt"
    )

    parser.add_argument(
        "-w", "--wait",
        action="store_true",
        help="Wait until image is available (or failed)"
    )

    args = parser.parse_args()

    create_image(args)


if __name__ == "__main__":
    sys.exit(main())