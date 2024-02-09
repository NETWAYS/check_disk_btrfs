#!/usr/bin/env python3

import unittest
import unittest.mock as mock
import sys

sys.path.append('..')


from check_disk_btrfs import cli
from check_disk_btrfs import get_size_overall
from check_disk_btrfs import parse_output
from check_disk_btrfs import parse_scrub
from check_disk_btrfs import parse_missing
from check_disk_btrfs import find_hr_bytes
from check_disk_btrfs import run_cmd
from check_disk_btrfs import main

testdata_fs_usage = """
Overall:
    Device size:		       10737418240
    Device allocated:                   2172649472
    Device unallocated:                 8564768768
    Device missing:                              0
    Used:                                   524288
    Free (estimated):                   8572895232	(min: 4290510848)
    Data ratio:                               1.00
    Metadata ratio:                           2.00
    Global reserve:                       16777216	(used: 0)

Data,single: Size:8388608, Used:262144
   /dev/sdb	   8388608

Metadata,DUP: Size:1073741824, Used:114688
   /dev/sdb	2147483648

System,DUP: Size:8388608, Used:16384
   /dev/sdb	  16777216

Unallocated:
   /dev/sdb	8564768768
""".splitlines()

testdata_device = """
Label: none  uuid: fdbb50c2-f155-4ef5-9ae8-c3ec57e2bcfd
	Total devices 2 FS bytes used 128.00KiB
	devid    1 size 1022.00MiB used 220.00MiB path /dev/nbd0p1
	devid    2 size 1022.00MiB used 208.00MiB path /dev/nbd1p1

""".splitlines()

testdata_device_missing = """
Label: none  uuid: fdbb50c2-f155-4ef5-9ae8-c3ec57e2bcfd
	Total devices 2 FS bytes used 128.00KiB
	devid    1 size 1022.00MiB used 220.00MiB path /dev/nbd0p1
	*** Some devices missing

""".splitlines()

testdata_scrub_noerror = """
UUID:             deb3ff35-a424-4edb-9673-e0514cef2cb0
Scrub started:    Tue Jan 10 09:58:05 2023
Status:           finished
Duration:         2:16:04
Total to scrub:   1.62TiB
Rate:             208.45MiB/s
Error summary:    no errors found

""".splitlines()

testdata_scrub_error = """
scrub status for <UUID>
    scrub started at Thu Dec 25 15:19:22 2014 and was aborted after 89882 seconds
    total bytes scrubbed: 1.87TiB with 4 errors
    error details: csum=4
    corrected errors: 0, uncorrectable errors: 4, unverified errors: 0

""".splitlines()


testdata_issue_13 = """
Overall:
    Device size:                     4000797868032
    Device allocated:                 942829207552
    Device unallocated:              3057968660480
    Device missing:                              0
    Device slack:                                0
    Used:                             934821470208
    Free (estimated):                1531379535872      (min: 1531379535872)
    Free (statfs, df):               1531378462720
    Data ratio:                               2.00
    Metadata ratio:                           2.00
    Global reserve:                      485900288      (used: 0)
    Multiple profiles:                          no

Data,RAID1: Size:469225177088, Used:466829971456 (99.49%)
   /dev/sda     469225177088
   /dev/sdb     469225177088

Metadata,RAID1: Size:2147483648, Used:580681728 (27.04%)
   /dev/sda     2147483648
   /dev/sdb     2147483648

System,RAID1: Size:41943040, Used:81920 (0.20%)
   /dev/sda       41943040
   /dev/sdb       41943040

Unallocated:
   /dev/sda     1528984330240
   /dev/sdb     1528984330240
""".splitlines()

class CLITesting(unittest.TestCase):

    def test_cli_arguments(self):
        actual = cli(['--sudo', '-t', '15', '-v'])
        self.assertTrue(actual.sudo)
        self.assertEqual(actual.timeout, 15)
        self.assertTrue(actual.verbose)

        actual = cli(['--no-sudo'])
        self.assertFalse(actual.sudo)
        self.assertFalse(actual.verbose)

        actual = cli(['--unallocated'])
        self.assertTrue(actual.unallocated)

        actual = cli(['--no-unallocated'])
        self.assertFalse(actual.unallocated)

class UtilTesting(unittest.TestCase):

    def test_get_size_overall(self):
        actual = get_size_overall(testdata_fs_usage)
        expected = '10737418240'
        self.assertEqual(actual, expected)

    def test_parse_output(self):
        actual = parse_output(testdata_fs_usage)
        expected = {'Data,single': ('8388608', '262144'), 'Metadata,DUP': ('1073741824', '114688'), 'System,DUP': ('8388608', '16384')}
        self.assertEqual(actual, expected)

    def test_find_hr_bytes(self):
        actual = find_hr_bytes('8388608', '262144')
        expected = ('MB', 8.0, 0.25)
        self.assertEqual(actual, expected)

    def test_no_missing_device(self):
        actual = parse_missing(testdata_device)
        self.assertFalse(actual)

    def test_missing_device(self):
        actual = parse_missing(testdata_device_missing)
        self.assertTrue(actual)

    def test_scrub_no_error(self):
        actual = parse_scrub(testdata_scrub_noerror)
        self.assertFalse(actual)

    def test_scrub_error(self):
        actual = parse_scrub(testdata_scrub_error)
        self.assertTrue(actual)

    def test_parse_output_issue_13(self):
        actual = parse_output(testdata_issue_13)
        expected = {'Data,RAID1': ('469225177088', '466829971456'), 'Metadata,RAID1': ('2147483648', '580681728'), 'System,RAID1': ('41943040', '81920')}
        self.assertEqual(actual, expected)

class RunTesting(unittest.TestCase):

    @mock.patch('check_disk_btrfs.Popen')
    def test_run_test(self, mock_open):

        c = mock.MagicMock()
        c.communicate.return_value = (b'unit\ntest', b'stderr')
        c.returncode = 0
        mock_open.return_value = c

        expected = ['unit', 'test']
        actual = run_cmd('/sudo', '/mydisk', 10, True, ['filesystem', 'show', '/mydisk'])

        self.assertEqual(actual, expected)

    @mock.patch('check_disk_btrfs.Popen')
    def test_run_test_runtimeerror(self, mock_open):

        c = mock.MagicMock()
        c.communicate.return_value = (b'stdout', b'stderr')
        c.returncode = 2
        mock_open.return_value = c

        with self.assertRaises(RuntimeError) as context:
            run_cmd('/sudo', '/mydisk', 10, True, ['filesystem', 'show', '/mydisk'])


class MainTesting(unittest.TestCase):

    @mock.patch('check_disk_btrfs.check_usage')
    @mock.patch('check_disk_btrfs.check_missing_device')
    @mock.patch('check_disk_btrfs.check_scrub_error')
    def test_main(self, mock_scrub, mock_miss, mock_use):
        mock_scrub.return_value = {}
        mock_miss.return_value = {}
        mock_use.return_value = {}

        args = cli(['--sudo', '-c', '1', '-v'])
        actual = main(args)

        self.assertEqual(actual, 0)


    @mock.patch('check_disk_btrfs.check_usage')
    @mock.patch('check_disk_btrfs.check_missing_device')
    @mock.patch('check_disk_btrfs.check_scrub_error')
    def test_main_issue_13(self, mock_scrub, mock_miss, mock_use):
        mock_scrub.return_value = {}
        mock_miss.return_value = {}
        mock_use.return_value = testdata_issue_13

        args = cli(['--no-sudo', '-w', '30', '-c', '40', '-v', '--missing', '--error'])
        actual = main(args)

        self.assertEqual(actual, 0)

if __name__ == '__main__':
    unittest.main()
