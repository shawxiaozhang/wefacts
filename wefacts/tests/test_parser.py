# # from unittest import TestCase
# #
# # import wefacts
# #
# #
# # class TestParser(TestCase):
# #     def test_is_string(self):
# #         # s = wefacts.
# #         s = '321'
# #         self.assertTrue(isinstance(s, basestring))
#
#
# def test_sfo():
#     # SFO Airport
#     rec = parse_raw_lite('724940-23234', 2017, 2, 6, 2, 6)
#     # y, m, d, h, oat, dt, slp, wd, ws, sky, ppt, ppt6 = \
#     row_num, _ = rec.shape
#     for day in xrange(row_num/24):
#         y, m, d = rec[day*24, 0:3]
#         oats = rec[day*24:(day+1)*24, 4]*0.1
#         winds = rec[day*24:(day+1)*24, 8]
#         # print '%d-%02d-%02d T %.1f %.1f %.1f Wind %.1f %.1f %.1f ' \
#         #       % (y, m, d, min(oats), max(oats), np.mean(oats), min(winds), max(winds), np.mean(winds))
#     print rec
#
#
# def test_sfo1():
#     # redundant 20170101
#     rec = parse_raw_lite('724940-test1', 2017, 1, 2, 1, 2)
#     row_num, _ = rec.shape
#     for day in xrange(row_num/24):
#         y, m, d = rec[day*24, 0:3]
#         oats = rec[day*24:(day+1)*24, 4]*0.1
#         winds = rec[day*24:(day+1)*24, 8]
#         # print '%d-%02d-%02d T %.1f %.1f %.1f Wind %.1f %.1f %.1f ' \
#         #       % (y, m, d, min(oats), max(oats), np.mean(oats), min(winds), max(winds), np.mean(winds))
#     print rec
#
#
# def test_sfo2():
#     # missing 20170101
#     rec = parse_raw_lite('724940-test2', 2017, 1, 2, 1, 2)
#     row_num, _ = rec.shape
#     for day in xrange(row_num/24):
#         y, m, d = rec[day*24, 0:3]
#         oats = rec[day*24:(day+1)*24, 4]*0.1
#         winds = rec[day*24:(day+1)*24, 8]
#         # print '%d-%02d-%02d T %.1f %.1f %.1f Wind %.1f %.1f %.1f ' \
#         #       % (y, m, d, min(oats), max(oats), np.mean(oats), min(winds), max(winds), np.mean(winds))
#     print rec
#
#
# def test_sfo3():
#     # missing hours in 20170102
#     rec = parse_raw_lite('724940-test3', 2017, 1, 2, 1, 2)
#     row_num, _ = rec.shape
#     for day in xrange(row_num/24):
#         y, m, d = rec[day*24, 0:3]
#         oats = rec[day*24:(day+1)*24, 4]*0.1
#         winds = rec[day*24:(day+1)*24, 8]
#         # print '%d-%02d-%02d T %.1f %.1f %.1f Wind %.1f %.1f %.1f ' \
#         #       % (y, m, d, min(oats), max(oats), np.mean(oats), min(winds), max(winds), np.mean(winds))
#     print rec
#
# if __name__ == '__main__':
#     # test_sfo()
#     test_sfo1()
#     test_sfo2()
#     test_sfo3()