check_disk_brtfs
================
 
Check BTRFS formatted filesystems and its special attributes.

Requires sudo permissions for the icinga/nagios user executing btrfs
command.

Important: Only permit `filesystem df /*`, and no other manipulation
options!!!

    icinga ALL=(ALL) NOPASSWD: /usr/sbin/btrfs filesystem df /*

    
### Usage

    check_disk_btrfs -f <filesystem> [-h|-v] [-w <warn_threshold in %> -c
    <crit_threshold in %>]


Options:

    -f|--filesystem
        btrfs filesystem to check (e.g. /)

    -w|--warning
        warning threshold in percent (global)

    -c|--critical
        critical threshold in percent (global)

    -h|--help
        print help page

    -v|--verbose
        print verbose output
