#!/bin/env python

import unittest


class PrinterBasicTestCase(unittest.TestCase):

    def setUp(self):
        from PolePrinter import LX300
        self.p = LX300()

    def tearDown(self):
        del self.p

    def test_get_printer_brand(self):
        self.assertEqual('Epson', self.p.brand)

    def test_get_printer_model(self):
        self.assertEqual('LX300', self.p.model)


class LX300CommandTestCase(unittest.TestCase):

    def setUp(self):
        from PolePrinter import LX300
        self.p = LX300()

    def tearDown(self):
        del self.p

    def test_initialize_printer(self):
        self.p.initialize_printer()
        self.assertEqual(chr(64), self.p.raw_buffer)

    def test_carriage_return(self):
        self.p.carriage_return()
        self.assertEqual(chr(13), self.p.raw_buffer)

    def test_one_line_feed(self):
        self.p.line_feed()
        self.assertEqual(chr(10), self.p.raw_buffer)

    def test_two_line_feed(self):
        self.p.line_feed(2)
        self.assertEqual(chr(10) * 2, self.p.raw_buffer)

    def test_select_condensed_mode(self):
        self.p.select_condensed_mode()
        self.assertEqual(chr(20) + chr(15), self.p.raw_buffer)

    def test_unset_condensed_mode(self):
        self.p.cancel_condensed_mode()
        self.assertEqual(chr(18), self.p.raw_buffer)

    def test_set_doublewith_mode(self):
        self.p.select_doublewith_mode()
        self.assertEqual(chr(18) + chr(14), self.p.raw_buffer)

    def test_unset_doublewith_mode(self):
        self.p.cancel_doublewith_mode()
        self.assertEqual(chr(20), self.p.raw_buffer)

    def test_select_10_cpi(self):
        self.p.select_10_cpi()
        self.assertEqual(chr(80), self.p.raw_buffer)

    def test_carriage_return_and_one_line_feed(self):
        self.p.return_and_feed()
        self.assertEqual(chr(13) + chr(10), self.p.raw_buffer)

    def test_carriage_return_and_two_times(self):
        self.p.return_and_feed(2)
        self.assertEqual(chr(13) + chr(10) + chr(13) + chr(10), self.p.raw_buffer)

class LX300AppendTextTestCase(unittest.TestCase):

    def setUp(self):
        from PolePrinter import LX300
        self.p = LX300()

    def tearDown(self):
        del self.p

    def test_append_line(self):
        self.p.append('Simple line.')
        self.assertEqual('Simple line.', self.p.raw_buffer)

    def test_append_paragraph(self):
        self.p.append('First paragraph.')
        self.p.carriage_return()
        self.p.line_feed()
        self.p.append('Second paragraph.')
        self.assertEqual('First paragraph.\r\nSecond paragraph.', self.p.raw_buffer)

    def test_formating_text(self):
        self.p.append('{}. {}.', 'Foo', 'Bar')
        self.assertEqual('Foo. Bar.', self.p.raw_buffer)

    def test_clear_raw_text(self):
        self.p.append('Foo')
        self.p.clear_buffer()
        self.assertEqual('', self.p.raw_buffer)


class LX300LinesCounterTestCase(unittest.TestCase):

    def setUp(self):
        from PolePrinter import LX300
        self.p = LX300()

    def tearDown(self):
        del self.p

    def test_inc_line_counter_in_carriage_return(self):
        self.p.carriage_return()
        self.assertEqual(1, self.p.lines)

    def test_inc_line_counter_in_one_line_feed(self):
        self.p.line_feed()
        self.assertEqual(1, self.p.lines)

    def test_inc_line_counter_in_four_line_feed(self):
        self.p.line_feed(4)
        self.assertEqual(4, self.p.lines)

    def test_inc_line_counter_in_one_return_and_feed(self):
        self.p.return_and_feed()
        self.assertEqual(2, self.p.lines)

    def test_inc_line_counter_in_three_return_and_feed(self):
        self.p.return_and_feed(3)
        self.assertEqual(6, self.p.lines)

    def test_clear_line_counter(self):
        self.p.return_and_feed()
        self.p.clear_buffer()
        self.assertEqual(0, self.p.lines)

if __name__ == '__main__':
    unittest.main(verbosity=2)
