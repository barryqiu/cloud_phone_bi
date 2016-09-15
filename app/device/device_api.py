__author__ = 'barryqiu'

import urllib2
from .. import db
from ..models import AgentRecord
from sqlalchemy import and_
from flask import current_app as app


def get_agent_record_by_user_id(user_id, game_id=0):
    start_ids = []
    end_records = db.session.query(AgentRecord).filter(
        and_(AgentRecord.start_id > 0, AgentRecord.user_id == user_id)).all()

    for end_record in end_records:
        start_ids.append(end_record.start_id)

    if not game_id:
        user_records = AgentRecord.query.filter(
            and_(AgentRecord.type == 0, AgentRecord.user_id == user_id, AgentRecord.id.notin_(start_ids))).all()
    else:
        user_records = AgentRecord.query.filter(
            and_(AgentRecord.type == 0, AgentRecord.user_id == user_id, AgentRecord.game_id == game_id,
                 AgentRecord.id.notin_(start_ids))).all()

    return user_records


def get_agent_record_by_device_id(device_id):
    start_ids = []
    end_records = db.session.query(AgentRecord).filter(
        and_(AgentRecord.start_id > 0, AgentRecord.device_id == device_id)).all()

    for end_record in end_records:
        start_ids.append(end_record.start_id)

    user_record = AgentRecord.query.filter(
        and_(AgentRecord.type == 0, AgentRecord.device_id == device_id, AgentRecord.id.notin_(start_ids))).first()

    return user_record


def device_available(device):
    if app.config['DEBUG']:
        return True

    active_info = device.get_device_info(device.id, 0)
    if active_info and active_info.startswith("1"):
        return True
    return False

    # if not device.user_name or not device.password:
    #     return False
    #
    # url_top = "http://yunphoneclient.shinegame.cn"
    # url3 = "http://yunphoneclient.shinegame.cn/" + device.device_name + "/testconn"
    #
    # if app.config['TESTING']:
    #     url3 = "http://101.201.37.72/" + device.device_name + "/testconn"
    #
    # username = device.user_name
    # password = device.password
    # realm = "CloudPhone"
    #
    # auth = urllib2.HTTPDigestAuthHandler()
    # auth.add_password(realm, url_top, username, password)
    # opener = urllib2.build_opener(auth)
    # urllib2.install_opener(opener)
    #
    # # proxy
    # # proxy = urllib2.ProxyHandler({'http': 'proxy.tencent.com:8080'})
    # # opener = urllib2.build_opener(proxy)
    # # urllib2.install_opener(opener)
    #
    # try:
    #     # res_data = urllib2.urlopen(url3, timeout=1)
    #     headers = {'Host': 'yunphoneclient.shinegame.cn'}
    #     req = urllib2.Request(url3, headers=headers)
    #     res_data = urllib2.urlopen(req, timeout=1)
    #     app.logger.error("%s:%s" % (device.device_name, res_data.code))
    #     if res_data.code == 200:
    #         the_page = res_data.read()
    #         content = str.strip(the_page)
    #         if content.startswith("Phone is OK"):
    #             return True
    #     return False
    # except Exception as e:
    #     app.logger.error(device.device_name + "   " + e.message)
    #     return False
