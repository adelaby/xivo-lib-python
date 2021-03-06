# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+


from mock import Mock, patch
from unittest import TestCase

from .. import user_rights


USER_NAME = 'a_user'
USER_ID = 12
GROUP_ID = 42


@patch('xivo.user_rights.getpwnam')
@patch('os.setuid')
@patch('os.setgid')
@patch('os.initgroups')
class TestChangeUser(TestCase):

    def test_when_user_does_not_exist(self, initgroups, setgid, setuid, pwnam):
        pwnam.side_effect = KeyError

        self.assertRaises(SystemExit, user_rights.change_user, USER_NAME)

    def test_when_user_exists_but_cannot_change_user(self, initgroups, setgid, setuid, pwnam):
        pwnam.return_value = Mock(pw_uid=USER_ID)
        setuid.side_effect = OSError

        self.assertRaises(SystemExit, user_rights.change_user, USER_NAME)

        setuid.assert_called_once_with(USER_ID)

    def test_when_success(self, initgroups, setgid, setuid, pwnam):
        pwnam.return_value = Mock(pw_uid=USER_ID, pw_gid=GROUP_ID, pw_name=USER_NAME)

        user_rights.change_user(USER_NAME)

        pwnam.assert_called_once_with(USER_NAME)
        setuid.assert_called_once_with(USER_ID)
        setgid.assert_called_once_with(GROUP_ID)
        initgroups.assert_called_once_with(USER_NAME, GROUP_ID)
