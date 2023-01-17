check_disk_brtfs
================

Check BTRFS formatted filesystems and its special attributes.

## Setup

Requires Python 3 to be installed (version v2.1.1 is the last `check_disk_btrfs` version running on Python 2)

Requires sudo permissions for the icinga/nagios user executing btrfs command.
If you are running the plugin with sudo permissions already, set `--sudo` as command line parameter.

```
icinga ALL=(ALL) NOPASSWD: /usr/sbin/btrfs filesystem usage *
```

Requires the `btrfs-tools` packages to be installed (the package name may change depending on the distribution).

## Usage

```bash
usage: check_disk_btrfs [-h] [-S] [-t TIMEOUT] [-U] [-w THRESHOLD_WARNING] [-c THRESHOLD_CRITICAL] [-V VOLUME] [-v]
                        [--btrfs-path BTRFS_PATH] [--sudo-path SUDO_PATH] [-m] [-e]

options:
  -h, --help            show this help message and exit
  -S, --sudo            Use sudo
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout in seconds for the CheckPlugin (default 30)
  -U, --unallocated     Consider unallocated blocks by using overall size as total
  -w THRESHOLD_WARNING, --threshold-warning THRESHOLD_WARNING
                        Warning threshold in percent
  -c THRESHOLD_CRITICAL, --threshold-critical THRESHOLD_CRITICAL
                        Critical threshold in percent
  -V VOLUME, --volume VOLUME
                        Path to the Btrfs volume
  -v, --verbose         Increase verbosity
  --btrfs-path BTRFS_PATH
                        Specify the btrfs path to the executable
  --sudo-path SUDO_PATH
                        Specify the sudo path to the executable
  -m, --missing         Check for missing devices in RAID array
  -e, --error           Check for scrub errors in device
```

Path to the `sudo` and `btrfs` binaries can be also adjusted using Environment Variables:

```
SUDO=/usr/bin/sudo
BTRFS=/usr/sbin/btrfs
```


Example:

```
check_disk_btrfs -V / -w 30 -c 40

CRITICAL: 'Data, single': 47.59051% used (0.0GB/2.0GB) OK: 'System, single': 0.39063% used (0.0MB/4.0MB), 'GlobalReserve, single': 0.0% used (0.0MB/16.0MB), 'Metadata, single': 16.41809% used (43.0MB/264.0MB) | data_single_used=1025990656;30;40;; data_single_total=2155872256;30;40;; system_single_used=16384;30;40;; system_single_total=4194304;30;40;; globalreserve_single_used=0;30;40;; globalreserve_single_total=16777216;30;40;; metadata_single_used=45449216;30;40;; metadata_single_total=276824064;30;40;;
```

## Icinga 2 Integration

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
                "-m" = "$disk_btrfs_missing$"
                "-e" = "$disk_btrfs_errors$"
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
