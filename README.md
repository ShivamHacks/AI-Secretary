# Setup

## Local Dev Environment:

Log into git and EC2 to manage both from terminal:

Make sure that ~/.ssh/config looks like this:
```
Host github.com
  AddKeysToAgent yes
  IdentityFile <git file>

Host *.amazonaws.com
  AddKeysToAgent yes
  User ec2-user
  IdentityFile <AWS file>
```

Git instructions:
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

AWS instructions:
TODO

Now you can access git from the terminal and ssh into EC2.

## Cloud Backend

Follow the same git setup instructions so the server can pull from the
repo.

After deploying the EC2 instance, you need to make sure
