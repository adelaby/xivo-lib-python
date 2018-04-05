# -*- coding: utf-8 -*-
# Copyright (C) 2008-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

"""Tests for xivo.udev

Copyright (C) 2008-2010  Avencall

"""

__version__ = "$Revision$ $Date$"

import unittest
import logging

logging.basicConfig(level=logging.CRITICAL)

from xivo import udev


class TestRulesParser(unittest.TestCase):

    def test_iter_multilines(self):
        lines = [
            "# a comment\n",
            "  # a comment too, some blank lines follow\n",
            "\n",
            " \n",
            "\t\n",
            " \t \n",
            "a line\n",
            "\n",
            "a multiline\\\n",
            " and it continues here\n",
            "\n",
            "a multiline made \\\n",
            "of more than two \\\n",
            "lines\n",
            "\n",
            " \t a multiline that starts  \\\n",
            "with some spaces\n",
            "\n",
            "# a multiline comment\\\n",
            " that continues here \n",
            "\n",
            "This multiline is \\\n",
            "# not a comment\n",
            "\n",
            "can we parse this at end of file? \\\n"
        ]
        multilines = [
            "# a comment",
            "# a comment too, some blank lines follow",
            "",
            "",
            "",
            "",
            "a line",
            "",
            "a multiline and it continues here",
            "",
            "a multiline made of more than two lines",
            "",
            "a multiline that starts  with some spaces",
            "",
            "# a multiline comment that continues here ",
            "",
            "This multiline is # not a comment",
            "",
            "can we parse this at end of file? "
        ]

        calc_mlines = list(udev.iter_multilines(lines))

        for p, mline in enumerate(calc_mlines):
            self.assertEqual((p, mline), (p, multilines[p]))
        self.assertEqual(len(calc_mlines), len(multilines))
        self.assertEqual(calc_mlines, multilines)

    def test_parse_udev_rule(self):
        mline = 'SUBSYSTEM=="net", DRIVERS=="?*", ATTRS{address}=="00:04:55:e3:91:77", NAME="eth0"'
        recons = [
            ["", 'SUBSYSTEM', "", '==', "", 'net'],
            [", ", 'DRIVERS', "", '==', "", '?*'],
            [", ", 'ATTRS{address}', "", '==', "", '00:04:55:e3:91:77'],
            [", ", 'NAME', "", '=', "", 'eth0'],
        ]
        parsed = {
            'SUBSYSTEM': ['==', "net"],
            'DRIVERS': ['==', "?*"],
            'ATTRS': { 'address': ['==', "00:04:55:e3:91:77"] },
            'NAME': ['=', "eth0"]
        }
        result = udev.parse_rule(mline)
        self.assertEqual(parsed, result[0])
        self.assertEqual(recons, result[1])

    def test_base_attr_key_simple(self):
        self.assertEqual(udev.base_attr_key("kikoolol"), ("kikoolol", None))

    def test_base_attr_key_withattr(self):
        self.assertEqual(udev.base_attr_key("mdr{rotfl}"), ("mdr", "rotfl"))

    def test_base_attr_key_invalid(self):
        self.assertRaises(ValueError, udev.base_attr_key, "invalid{error")

    def test_replace_simple_op_values(self):
        recons = [
            ["", 'SUBSYSTEM', "", '==', "", 'net'],
            [", ", 'DRIVERS', "", '==', "", '?*'],
            [", ", 'ATTRS{address}', "", '==', "", '00:04:55:e3:91:77'],
            [", ", 'NAME', "", '=', "", 'eth0'],
        ]
        repl = {
            'NAME': ['=', "eth1"]
        }
        result_line = 'SUBSYSTEM=="net", DRIVERS=="?*", ATTRS{address}=="00:04:55:e3:91:77", NAME="eth1"'
        self.assertEqual(result_line, udev.replace_simple_op_values(recons, repl))

    def test_replace_simple(self):
        lines = [
            '# This file was automatically generated by the /lib/udev/write_net_rules\n',
            '# program, probably run by the persistent-net-generator.rules rules file.\n',
            '#\n',
            '# You can modify it, as long as you keep each rule on a single line.\n',
            '# MAC addresses must be written in lowercase.\n',
            '\n',
            'SUBSYSTEM=="net", DRIVERS=="?*", ATTRS{address}=="00:04:55:e3:91:77", NAME="eth0"\n',
            '\n',
            'SUBSYSTEM=="net", DRIVERS=="?*", ATTRS{address}=="00:0e:52:ab:42:1f", NAME="eth1"\n',
            '\n',
        ]
        match_repl_lst = [
            ({'NAME': ['=', "eth0"]}, {'NAME': ['=', "eth1"]}),
            ({'NAME': ['=', "eth1"]}, {'NAME': ['=', "eth0"]}),
        ]
        result_lines = [
            '# This file was automatically generated by the /lib/udev/write_net_rules\n',
            '# program, probably run by the persistent-net-generator.rules rules file.\n',
            '#\n',
            '# You can modify it, as long as you keep each rule on a single line.\n',
            '# MAC addresses must be written in lowercase.\n',
            '\n',
            'SUBSYSTEM=="net", DRIVERS=="?*", ATTRS{address}=="00:04:55:e3:91:77", NAME="eth1"\n',
            '\n',
            'SUBSYSTEM=="net", DRIVERS=="?*", ATTRS{address}=="00:0e:52:ab:42:1f", NAME="eth0"\n',
            '\n',
        ]
        self.assertEqual(result_lines, list(udev.replace_simple(lines, match_repl_lst)))


# import tracer
# import time
# tracer.enable_tofp(open("traces.%s" % time.time(), 'w'))
