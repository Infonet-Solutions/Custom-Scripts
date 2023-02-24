# NSWL

- nswl.service is a systemd script to manage the NSWL binary
- nswl_logrotate.sh is a bash script to help archiving NSWL logs


## nswl.service

- Compile variables in the `[Service]` section
- Put nswl.service in the `/usr/local/systemd/system/` folder
- Update systemd with the `systemctl daemon reload` command

## nswl_logrotate.sh

- Set variables according to your configuration
- Schedule script execution with `crontab`
