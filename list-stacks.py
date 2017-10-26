#!/usr/bin/env python3
import sys

import boto3


def list_stacks():
    cf = boto3.client("cloudformation")
    response = cf.describe_stacks()
    stacks = response["Stacks"]

    for each in stacks:
        print(each["StackName"])


def main():
    list_stacks()


if __name__ == "__main__":
    sys.exit(main())