# LinuxFamilyLink
FamilyLink like user limiting for Linux systems

It monitors logged in time, and bedtimes.  

*--kill* is optional.  Without it, it only does reporting.

### CRONTAB
```
*/5 * * * * /usr/sbin/usertime.py aaron max=240 bedtime=23:00-09:00 --kill
```
