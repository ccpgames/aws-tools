# aws-tools
Collection of tools for automating AWS related tasks

There are scripts to:
* create (and terminate) a number of machines
* list machines and their state
* run a command on all machines
* list CloudFormation stacks

Example:
```bash
python3 create-bot-machines.py --count 5 --wait
python3 list-bot-machines.py
python3 run.py --upload some-script.tgz "hostname;python3 do-something.sh"
python3 terminate-bot-machines.py
python3 list-machines.py
```

## create-bot-machines
Creates a number of machines, based off a given AMI. The machines are given
a *Bot* tag, and a *Name* tag with an index appended to the base tag.

#### --image *image* or -i *image*
The id of an AMI to use when launching the machines. The default is ami-785db401,
a standard Ubuntu 16.04 server.

#### --key *key* or -k *key*
The name of a key pair to use when launching the machines. The name must be the
name of an existing key, and you must have access to the corresponding .pem
file.

This argument is required.

#### --size size or -s *size*
The size, or instance type to launch. The default is t2.micro.

#### --security-group *name* or -c *name*
The name of the security group to apply to the instances. This argument is
required.

#### --count *N* or -n *N*
The number of instances to launch. The default is 1.

#### --tag *name* or -t *name*
The base tag for the machines. Each instance is given a tag with the key *Bot*
the given *name* as the value, as well as a *Name* tag of the form *name-ix*
(*name-1*, *name-2*, ...). The default name is run-bot.

#### --wait or -w
Wait until all machines are in the running state.

## list-bot-machines
Lists all the machines with the given tag, along with their state.

#### --tag *name* or -t *name*
The base tag given when the machines were created (see **create-machines**).
The default is run-bot.

## terminate-bot-machines
Terminates all machines with the given tag. The machines found with the
appropriate tag are listed out for you to confirm before they are terminated.

#### --tag *name* or -t *name*
The base tag given when the machines were created (see **create-machines**).
The default is run-bot.

## run
Runs a given command on each machine with the appropriate tag. You can
optionally upload a file to the machine before the command is run - if that
file is a .tgz file it is automatically unpacked.

Note that you should wait until all the machines are in a running state before
issuing this command. You can verify that with **list-machines**.

The key file specified when the machines were created must be available in the
working directory.

#### --upload *file* or -u *file*
File to upload to each machine before running the command. If it is a .tgz
file it is automatically unpacked.

#### --tag *name* or -t *name*
The base tag given when the machines were created (see **create-machines**).
The default is run-bot.

#### command
The command to run (a positional argument, no dashes). Enclose in quotes if
there are spaces in the command.

## list-machines

Lists all machines on your account, grouped by state.

## list-stacks

Lists all CloudFormation stacks on your account.

## stack-status

Shows the status of the given stack and its resources.

#### --stack-name *stack* or -s *name*

The name of the stack.