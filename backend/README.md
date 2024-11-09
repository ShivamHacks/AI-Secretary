# First Time Setup

1. Make all scripts executable: `chmod +x scripts/*.sh`
2. Set up virtual env: `python3 -m venv .venv`

Now, everytime you want to work on the project, run:

`./scripts/setup-workspace.sh`

This will put you in a virtual environment. Anytime you sync from the remote repository, this command will also update the dependencies.

When you want to exit the virtual environment, run `deactivate`.

Anytime you want to work on the project, run `source .venv/bin/activate`.

# Running Server

`./scripts/run-local.sh`

# Miscellaneous Notes

To send any local credential files (no longer needed):
`scp <file> ec2-user@ec2-3-141-106-24.us-east-2.compute.amazonaws.com:<path>`

## Setting up HTTPS (already done)

1. Get a public domain (used AWS Route53) (took 10 minutes for domain to register)
2. Link public domain to ec2 http address via Route53 hosted zone - create an A record
3. Use the setup-https script to setup https
