#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/12/10 15:36
# @Author : Sai
# @File : views_if
# @Software: PyCharm
import time
from django.http import JsonResponse
from sign.models import Event, Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError


# 添加发布会接口
def add_event(request):
    eid = request.POST.get('eid', '')                          # 发布会id
    name = request.POST.get('name', '')                        # 发布会标题
    limit = request.POST.get('limit', '')                      # 限制人数
    status = request.POST.get('status', '')                    # 状态
    address = request.POST.get('address', '')                  # 地址
    start_time = request.POST.get('start_time', '')            # 发布会时间

    # 非空判断
    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse({'status': 10021,
                             'message': 'parameter error'})
    # 发布会id重复校验
    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse(
            {'status': 10022,
             'message': 'event id already exists'})

    # 发布会名称重复校验
    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status': 10023,
                             'message': 'event name already exists'})
    # 默认发布会状态为1
    if status == '':
        status = 1

    try:
        Event.objects.create(
            id=eid,
            name=name,
            limit=limit,
            address=address,
            status=int(status),
            start_time=start_time)
    except ValidationError:
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status': 10024,
                             'message': error})

    return JsonResponse({'status': 200,
                         'message': 'add event success'})


# 发布会查询
def get_event_list(request):

    eid = request.GET.get("eid", "")      # 发布会id
    name = request.GET.get("name", "")    # 发布会名称

    # 非空校验
    if eid == '' and name == '':
        return JsonResponse({'status': 10021, 'message': 'parameter error'})

    if eid != '':
        event = dict()
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse(
                {'status': 10022, 'message': 'query result is empty'})
        else:
            event['eid'] = result.id
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse(
                {'status': 200, 'message': 'success', 'data': event})

    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = dict()
                event['eid'] = r.id
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse(
                {'status': 200, 'message': 'success', 'data': datas})
        else:
            return JsonResponse(
                {'status': 10022, 'message': 'query result is empty'})


# 添加嘉宾接口
def add_guest(request):
    eid = request.POST.get('eid', '')               # 关联发布会id
    realname = request.POST.get('realname', '')     # 姓名
    phone = request.POST.get('phone', '')           # 手机号
    email = request.POST.get('email', '')           # 邮箱

    # 非空校验
    if eid == '' or realname == '' or phone == '':
        return JsonResponse({'status': 10021,
                             'message': 'parameter error'})

    # 校验发布会是否存在
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status': 10022,
                             'message': 'event id null'})

    # 校验发布会状态是否为1
    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status': 10023,
                             'message': 'event status is not available'})

    event_limit = Event.objects.get(id=eid).limit      # 发布会最大人数
    guest_limit = Guest.objects.filter(id=eid)         # 发布会已有嘉宾人数

    # 校验发布会人数是否超出
    if len(guest_limit) >= event_limit:
        return JsonResponse({'status': 10025,
                             'message': 'event number is full'})

    event_time = Event.objects.get(id=eid).start_time                   # 发布会时间
    timearray = time.strptime(
        str(event_time),
        "%Y-%m-%d %H:%M:%S")     # 将发布会时间转换成struct_time的形式
    # 做换为时间戳
    e_time = int(time.mktime(timearray))

    now_time = str(time.time())                                         # 当前时间
    # 截取当前时间.前的字符
    ntime = now_time.split(".")[0]
    # 转换为int类型
    n_time = int(ntime)

    # 校验当前时间是否超过发布会开始时间
    if n_time >= e_time:
        return JsonResponse({'status': 10025, 'message': 'event has started'})

    try:
        Guest.objects.create(
            realname=realname,
            phone=int(phone),
            email=email,
            sign=0,
            event_id=int(eid))
    except IntegrityError:
        return JsonResponse({'status': 10026,
                             'message': 'the event guest phone number repeat'})

    return JsonResponse({'status': 200, 'message': 'add guest success'})
