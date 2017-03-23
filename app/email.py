# -*- coding: utf-8 -*-

from . import mail
from flask_mail import Message
from flask import render_template, current_app
from threading import Thread

def async_send_mail(app, subject, sender, recipients, body, html):
    msg = Message(subject=subject, recipients=recipients, sender=sender)
    msg.body = body
    msg.html = html
    with app.app_context():
        mail.send(msg)


def send_mail(subject, sender, recipients, prefix_template, **kwargs):
    body = render_template(prefix_template + '.txt', **kwargs)
    html = render_template(prefix_template + '.html', **kwargs)

    app = current_app._get_current_object()
    thr = Thread(target=async_send_mail, args=(app, subject, sender, recipients, body, html))
    thr.start()
    return thr
