# -*- coding: utf-8 -*-


import unittest
import os
from qiniu import Auth, put_data
import logging

logging.basicConfig(level=logging.INFO)


class QINIUTestCase(unittest.TestCase):
    def setUp(self):
        self.q = Auth(os.getenv('QINIUAK'), os.getenv('QINIUSK'))

    def test_nokey(self):
        with self.assertRaises(ValueError):
           Auth(None, None).token('nokey')
        with self.assertRaises(ValueError):
            Auth('', '').token('nokey')

    def test_put(self):
        key = 'a\\b\\c"hello'
        data = 'hello baby!'
        token = self.q.upload_token('test')
        ret, info = put_data(token, key, data)
        logging.info(info)
        assert ret['key'] == key


