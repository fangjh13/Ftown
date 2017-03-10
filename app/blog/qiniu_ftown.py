# -*- coding: utf-8 -*-

import os
from qiniu import Auth, put_data


q = Auth(os.getenv('QINIUAK'), os.getenv('QINIUSK'))


def upload_picture(bucket_name, filename, data):
    token = q.upload_token(bucket_name)
    ret, info = put_data(token, filename, data)
    if ret is None:
        raise IOError('Can not upload file to qiniu')