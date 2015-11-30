from CCPRestSDK import REST
from flask import current_app as app

__author__ = 'barryqiu'


def send_smd(mobile, code, ttl):
    # init REST SDK
    serverIP = app.config['SMS_SERVER_IP']
    serverPort = app.config['SMS_SERVER_PORT']
    softVersion = app.config['SMS_SOFT_VERSION']
    accountSid = app.config['SMS_SID']
    accountToken = app.config['SMS_TOKEN']
    appId = app.config['SMS_APP_ID']
    tempId = app.config['SMS_TMPLATE_ID']

    rest = REST(serverIP, serverPort, softVersion)
    rest.setAccount(accountSid, accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(mobile, {code}, tempId)
    for k, v in result.iteritems():

        if k == 'templateSMS':
            for k, s in v.iteritems():
                print '%s:%s' % (k, s)
        else:
            print '%s:%s' % (k, v)
