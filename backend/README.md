# First Time Setup

1. Make all scripts executable: `chmod +x scripts/*.sh`
2. Set up virtual env: `python3 -m venv .venv`

Now, everytime you want to work on the project, run:

`./scripts/setup-workspace.sh`

This will put you in a virtual environment. Anytime you sync from
the remote repository, this command will also update the dependencies.

When you want to exit the virtual environment, run `deactivate`.

# Running Server

`./scripts/run-local.sh`

# Architecture Notes

1. `server.py` is the main entry point, server requests come there
2. For each user, there is a `chat.py` object. This manages the chat.
3. Each chat object uses tools from the `tools` folder.
4. When the user's state changes throughout a chat message (e.g. chat
stream chunk, event created from tool call), the database from `database/`
folder updates the local cache. When the chat message is complete, the
database updates the remote database. The local cache is always sent to the
user, so it's possible the user's state is "ahead" of the remote database.
This is an important preformance optimization, otherwise if we waited to send
the user the updated state until all of the remote database updates finished,
it would take a long time (imagine a chat message that creates 100 events).
This also lets the chat be used offline, without requiring access to the remote
database or google calendar.

## Automated Tests

`chat_tests.py` can help 

# Miscellaneous Notes

To send any local credential files (no longer needed):
`scp <file> ec2-user@ec2-3-141-106-24.us-east-2.compute.amazonaws.com:<path>`

## Setting up HTTPS (already done)

1. Get a public domain (used AWS Route53) (took 10 minutes for domain to register)
2. Link public domain to ec2 http address via Route53 hosted zone - create an A record
3. Use the setup-https script to setup https
