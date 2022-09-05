import unittest

import importlib.machinery
import importlib.util

# Import check_disk_btrfs script as module
loader = importlib.machinery.SourceFileLoader('btrfs', 'check_disk_btrfs')
spec = importlib.util.spec_from_loader('btrfs', loader)
btrfs = importlib.util.module_from_spec(spec)
loader.exec_module(btrfs)


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

class Testing(unittest.TestCase):

    def test_get_size_overall(self):
        actual = btrfs.get_size_overall(testdata_fs_usage)
        expected = '10737418240'
        self.assertEqual(actual, expected)

    def test_parse_output(self):
        actual = btrfs.parse_output(testdata_fs_usage)
        expected = {'Data,single': ('8388608', '262144'), 'Metadata,DUP': ('1073741824', '114688'), 'System,DUP': ('8388608', '16384')}
        self.assertEqual(actual, expected)

    def test_find_hr_bytes(self):
        actual = btrfs.find_hr_bytes('8388608', '262144')
        expected = ('MB', 8.0, 0.25)
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
