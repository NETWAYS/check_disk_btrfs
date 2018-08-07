check_disk_brtfs
================

Check BTRFS formatted filesystems and its special attributes.

Requires sudo permissions for the icinga/nagios user executing btrfs
command. If you are running the plugin with sudo permissions already,
set `--sudo=0` as command line parameter.

```
icinga ALL=(ALL) NOPASSWD: /usr/sbin/btrfs filesystem usage *
```

### Usage

```
usage: check_disk_btrfs [-h] [-S SUDO] [-t TIMEOUT] [-U UNALLOCATED]
                        [-w THRESHOLD_WARNING] [-c THRESHOLD_CRITICAL]
                        [-V VOLUME] [-v]

check_disk_btrfs (Version: 2.1.0)

optional arguments:
  -h, --help            show this help message and exit
  -S SUDO, --sudo SUDO  use sudo
  -t TIMEOUT, --timeout TIMEOUT
                        plugin timeout
  -U UNALLOCATED, --unallocated UNALLOCATED
                        consider unallocated blocks by using overall size as
                        total
  -w THRESHOLD_WARNING, --threshold-warning THRESHOLD_WARNING
                        warning threshold in percent
  -c THRESHOLD_CRITICAL, --threshold-critical THRESHOLD_CRITICAL
                        critical threshold in percent
  -V VOLUME, --volume VOLUME
                        btrfs volume
  -v, --verbose         increase output verbosity
```

Example:

```
check_disk_btrfs -V / -w 30 -c 40

CRITICAL: 'Data, single': 47.59051% used (0.0GB/2.0GB) OK: 'System, single': 0.39063% used (0.0MB/4.0MB), 'GlobalReserve, single': 0.0% used (0.0MB/16.0MB), 'Metadata, single': 16.41809% used (43.0MB/264.0MB) | data_single_used=1025990656;30;40;; data_single_total=2155872256;30;40;; system_single_used=16384;30;40;; system_single_total=4194304;30;40;; globalreserve_single_used=0;30;40;; globalreserve_single_total=16777216;30;40;; metadata_single_used=45449216;30;40;; metadata_single_total=276824064;30;40;;
```

### Icinga 2 Integration

Example CheckCommand, Host and Service objects:

```
object CheckCommand "disk_btrfs" {
        import "plugin-check-command"

        command = [ PluginDir + "/check_disk_btrfs" ]

        arguments = {
                "-V" = "$disk_btrfs_volume$"
                "-w" = "$disk_btrfs_warn$"
                "-c" = "$disk_btrfs_crit$"
                "-U" = "$disk_btrfs_unallocated$"
                "-s" = "$disk_btrfs_sudo$"
        }
}

object Host "btrfs-host" {
        address = "127.0.0.1"
        check_command = "hostalive"
}

apply Service "disk /" {
        check_command = "disk_btrfs"
        vars.disk_btrfs_volume = "/"
        vars.disk_btrfs_warn = 30
        vars.disk_btrfs_crit = 40

        assign where match("btrfs*", host.name)
}
```

