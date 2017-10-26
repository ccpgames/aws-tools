#!/usr/bin/env python3
import argparse
import os
import signal
import subprocess
import sys

import boto3


def run_command(cmd, output_stream):

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    output, errors = process.communicate()
    if output:
        output_stream.write(output.decode())


def get_machines(args):
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "tag:Bot",
                "Values": [args.tag]
            },
            {
                "Name": "instance-state-name",
                "Values": ["running"]
            }
        ]
    )

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
            instance_id = instance["InstanceId"]
            dns = instance["PublicDnsName"]
            key = instance["KeyName"]
            machines.append({"InstanceId": instance_id, "Name": name, "PublicDnsName": dns, "KeyName": key})

    return machines



def run_command_on_machine(args, machine, output_stream):
    dns_name = machine["PublicDnsName"]
    key_name = machine["KeyName"]
    cmd_template = "ssh -t -i %s.pem ubuntu@%s \"stty isig intr ^N -echoctl ; trap '/bin/true' SIGINT; %s\""
    cmd = cmd_template % (key_name, dns_name, args.command)

    if args.upload:
        output_stream.write("Copying %s to %s\n" % (args.upload, dns_name))
        dest = os.path.basename(args.upload)
        scp = "scp -i %s.pem %s ubuntu@%s:%s" % \
              (key_name, args.upload, dns_name, dest)
        run_command(scp, output_stream)
        print(dest)
        if dest.endswith(".tgz"):
            output_stream.write("Unpacking %s\n" % dest)
            unpack = "ssh -i %s.pem ubuntu@%s \"tar -xvzf %s\"" % (key_name, dns_name, dest)
            print(unpack)
            run_command(unpack, output_stream)

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return process


def run_on_machines(args):
    machines = get_machines(args)
    if not machines:
        print("No machines found")
        return

    processes = []

    try:
        for machine in machines:
            filename = machine["Name"] + ".log"
            output_for_machine = open(filename, "w")
            p = run_command_on_machine(args, machine, output_for_machine)
            processes.append((p, output_for_machine))

        while processes:
            live_processes = []
            for process, output_stream in processes:
                while process.returncode is None:
                    try:
                        output, errors = process.communicate(timeout=0.1)
                        if output:
                            output_stream.write(output.decode())
                        if errors:
                            output_stream.write(errors.decode())
                    except subprocess.TimeoutExpired:
                        live_processes.append((process, output_stream))

            processes = live_processes
    except KeyboardInterrupt:
        print("Keyboard interrupt - stopping processes")
        for p, output_stream in processes:
            p.send_signal(signal.SIGINT)
            print("Waiting for process %d" % p.pid)
            output, errors = p.communicate()
            if output:
                output_stream.write(output.decode())
            if errors:
                output_stream.write(errors.decode())


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-u", "--upload",
        help="File to upload to the machine before running the command"
    )
    parser.add_argument(
        "-t", "--tag",
        default="run-bot",
        help="The base name for a Name tag"
    )
    parser.add_argument(
        "command",
        help="The command to run on each machine"
    )
    args = parser.parse_args()

    run_on_machines(args)


if __name__ == "__main__":
    sys.exit(main())