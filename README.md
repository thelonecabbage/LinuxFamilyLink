# LinuxFamilyLink
FamilyLink like user limiting for Linux systems

### CRONTAB
```
*/5 * * * * /usr/sbin/usertime.py aaron max=240 bedtime=23:00-09:00 --kill
```
