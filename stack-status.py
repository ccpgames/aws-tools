#!/usr/bin/env python3
import argparse
import sys

import boto3


def lb_status(lb):
    print("Load balancers:")
    elb = boto3.client("elb")
    for each in lb:
        elb_id = each["PhysicalResourceId"]
        response = elb.describe_load_balancers(LoadBalancerNames=[elb_id])
        data = response["LoadBalancerDescriptions"][0]

        print(each["LogicalResourceId"], data["DNSName"])

        response = elb.describe_instance_health(
            LoadBalancerName=each["PhysicalResourceId"]
        )
        instance_states = response["InstanceStates"]
        for instance in instance_states:
            state = instance["State"]
            instance_id = instance["InstanceId"]
            print(instance_id, state)

    print()


def ec2_instances_status(ec2_instances):
    ec2 = boto3.client("ec2")
    instance_ids = [x["PhysicalResourceId"] for x in ec2_instances]
    response = ec2.describe_instances(
        InstanceIds=instance_ids
    )

    print("EC2 instances:")
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
            address = instance.get("PublicIpAddress", "")
            if not address:
                address = instance.get("PrivateIpAddress", "")
            instance_type = instance["InstanceType"]
            zone = instance["Placement"]["AvailabilityZone"]
            print(name, instance_type, state, instance_id, address, zone)

    print()
    #pprint.pprint(reservations)

def stack_status(args):
    cf = boto3.client("cloudformation")
    response = cf.describe_stack_resources(
        StackName=args.stack_name
    )

    resources = response["StackResources"]

    resources_by_type = {}
    for each in resources:
        resource_type = each["ResourceType"]
        l = resources_by_type.get(resource_type, [])
        l.append(each)
        resources_by_type[resource_type] = l

    lb = resources_by_type.get("AWS::ElasticLoadBalancing::LoadBalancer", None)
    if lb is not None:
        del resources_by_type["AWS::ElasticLoadBalancing::LoadBalancer"]

    ec2_instances = resources_by_type.get("AWS::EC2::Instance", None)
    if ec2_instances is not None:
        del resources_by_type["AWS::EC2::Instance"]

    print("Resources belonging to", args.stack_name)
    print()

    if lb:
        lb_status(lb)
    if ec2_instances:
        ec2_instances_status(ec2_instances)

    for each in resources_by_type.keys():
        print(len(resources_by_type[each]), each)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-s", "--stack-name",
        help="The name of a CloudFormation stack",
        required=True
    )

    args = parser.parse_args()

    stack_status(args)


if __name__ == "__main__":
    sys.exit(main())