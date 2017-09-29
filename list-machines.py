import sys

import boto3


def list_machines():
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances()

    machines = []
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
            machines.append((state, name, instance["InstanceId"]))

    machines.sort()
    current_state = None
    for each in machines:
        state, name, instance_id = each
        if state != current_state:
            if current_state:
                print()
            current_state = state
            print("State:", current_state)
        print(instance_id, name)


def main():
    list_machines()


if __name__ == "__main__":
    sys.exit(main())