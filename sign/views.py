from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
def index(request):
    return render(request, 'index.html')


# 登录动作
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        # if username == 'admin' and password == 'admin123':
        #     response = HttpResponseRedirect('/event_manage/')
        if username != '' and password != '':
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)  # 登录
                # response.set_cookie('user', username, 3600)  # 添加浏览器cookie
                request.session['user'] = username  # 将session信息放到浏览器
                response = HttpResponseRedirect('/event_manage/')  # 登录成功后实现重定向
                return response
            else:
                return render(
                    request, 'index.html', {'error': 'username or password error!'})
        else:
            return render(
                request, 'index.html', {'error': 'username or password null!'})


# 发布会管理
@login_required
def event_manage(request):
    event_list = Event.objects.all()
    # username = request.COOKIES.get('user', '')  # 读取浏览器cookie
    username = request.session.get('user', '')  # 读取浏览器session
    # 分页
    pageinator = Paginator(event_list, 2)
    page = request.GET.get('page')
    try:
        contacts = pageinator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，取第一页数据
        contacts = pageinator.page(1)
    except EmptyPage:
        # 如果page不在范围内，取最后一页数据
        contacts = pageinator.page(pageinator.num_pages)
    return render(request, "event_manage.html", {"user": username,
                                                 "events": contacts})


# 发布会名称搜索
@login_required
def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get("name", '')
    event_list = Event.objects.filter(name__contains=search_name)
    # 分页
    pageinator = Paginator(event_list, 2)
    page = request.GET.get('page')
    try:
        contacts = pageinator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，取第一页数据
        contacts = pageinator.page(1)
    except EmptyPage:
        # 如果page不在范围内，取最后一页数据
        contacts = pageinator.page(pageinator.num_pages)

    return render(request, "event_manage.html", {"user": username,
                                                 "events": contacts,
                                                 "name": search_name})


# 嘉宾管理
@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()
    # 分页
    pageinator = Paginator(guest_list, 2)
    page = request.GET.get('page')
    try:
        contacts = pageinator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，取第一页数据
        contacts = pageinator.page(1)
    except EmptyPage:
        # 如果page不在范围内，取最后一页数据
        contacts = pageinator.page(pageinator.num_pages)

    return render(request, "guest_manage.html", {"user": username,
                                                 "guests": contacts})


# 嘉宾手机号搜索
@login_required
def search_phone(request):
    username = request.session.get('user', '')
    search_phone = request.GET.get("phone", '')
    search_name_bytes = search_phone.encode(encoding="utf-8")
    guest_list = Guest.objects.filter(phone__contains=search_name_bytes)
    # 分页
    pageinator = Paginator(guest_list, 2)
    page = request.GET.get('page')
    try:
        contacts = pageinator.page(page)
    except PageNotAnInteger:
        # 如果page不是整数，取第一页数据
        contacts = pageinator.page(1)
    except EmptyPage:
        # 如果page不在范围内，取最后一页数据
        contacts = pageinator.page(pageinator.num_pages)
    return render(request, "guest_manage.html", {"user": username,
                                                 "guests": contacts,
                                                 "phone": search_phone})


# 签到
@login_required
def sign_index(request, eid):
    event = get_object_or_404(Event, id=eid)
    return render(request, 'sign_index.html', {'event': event})


# 签到动作
@login_required
def sign_index_action(request, eid):
    event = get_object_or_404(Event, id=eid)
    phone = request.POST.get('phone', '')
    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': 'phone error'})

    result = Guest.objects.filter(phone=phone, event_id=eid)
    if not result:
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': 'event id or phone error'})
    result = Guest.objects.get(phone=phone, event_id=eid)
    if result.sign:
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': 'user has sign in'})
    else:
        Guest.objects.filter(phone=phone, event_id=eid).update(sign='1')
        return render(request, 'sign_index.html', {'event': event,
                                                   'hint': 'sign in success',
                                                   'guest': result})


# 退出登录
@login_required
def logout(request):
    auth.logout(request)
    response = HttpResponseRedirect('/index/')
    return response
