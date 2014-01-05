#!/usr/bin/env python
# Copyright: 2014 (C) Alexander Vershilov <alexander.vershilov@gmail.com>
# License:  BSD

# Mail send wrapper, this program reads proper email in RFC 822 format
# and resend in to specified server, placing email inside attachement.
# If error occurs then email is sent via syslog ERROR

# HOWTO:
# In order to use this program you need to configure virtual recipient,
# see http://www.perlmonks.org/?node_id=1030830 for details.
# Basic idea if site will be down to have an alias:
#   redirect: /path/to/this/script
# In this file you may want to change:
#   70: send_email(msg["from"],["root@thinkpad"], msg["Subject"], str(msg) + str(t))
#        
#   here ["root@thinkpad"] is a list of recipients, and additional parameter may
#   be server URL
#
# Commented code in the bottom is for mailbox processing, it may be needed if
# pipe is used to resend messages.
# 
#  useStdIn variable exists to differ between pipe and stdin functionallity

import smtplib, os, sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase 
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import syslog

#parse email
import rfc822
import mailbox


useStdIn=True

def send_email(send_from, send_to, subject, text, server="localhost",port=24):
    assert type(send_to)   == list
    
    msg = MIMEMultipart()
    msg["From"] = send_from
    msg["To"]   = COMMASPACE.join(send_to)
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = subject

    # XXX: maybe we need another mutipart message type, and message encoding
    msg.attach(MIMEText("text"))

    part = MIMEBase('application', "octet-stream")
    part.set_payload( text )
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="mail.email"')
    msg.attach(part)

    try:
        smtp = smtplib.LMTP(server, port)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
    except:
        syslog.syslog(syslog.LOR_ERR, "Error sending email: " ++ msg.as_string())


if useStdIn:
    # one message approach
    msg = rfc822.Message(sys.stdin)
    t = os.read(sys.stdin)
    send_email(msg["from"],["root@thinkpad"], msg["Subject"], str(msg) + str(t))

else:
    # mailbox approach, should be used in pipe setup
    box = mailbox.mbox("/path/to/pipe", None, False);
    for m in box:
        send_email(m["From"],["root@thinkpad"], m["Subject"], str(m))
