from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
def index(request):
    return render(request, 'index.html')


# ��¼����
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        # if username == 'admin' and password == 'admin123':
        #     response = HttpResponseRedirect('/event_manage/')
        if username != '' and password != '':
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)  # ��¼
                # response.set_cookie('user', username, 3600)  # ��������cookie
                request.session['user'] = username  # ��session��Ϣ�ŵ������
                response = HttpResponseRedirect('/event_manage/')  # ��¼�ɹ���ʵ���ض���
                return response
            else:
                return render(
                    request, 'index.html', {'error': 'username or password error!'})
        else:
            return render(
                request, 'index.html', {'error': 'username or password null!'})


# ���������
@login_required
def event_manage(request):
    event_list = Event.objects.all()
    # username = request.COOKIES.get('user', '')  # ��ȡ�����cookie
    username = request.session.get('user', '')  # ��ȡ�����session
    # ��ҳ
    pageinator = Paginator(event_list, 2)
    page = request.GET.get('page')
    try:
        contacts = pageinator.page(page)
    except PageNotAnInteger:
        # ���page����������ȡ��һҳ����
        contacts = pageinator.page(1)
    except EmptyPage:
        # ���page���ڷ�Χ�ڣ�ȡ���һҳ����
        contacts = pageinator.page(pageinator.num_pages)
    return render(request, "event_manage.html", {"user": username,
                                                 "events": contacts})


# ��������������
@login_required
def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get("name", '')
    event_list = Event.objects.filter(name__contains=search_name)
    # ��ҳ
    pageinator = Paginator(event_list, 2)
    page = request.GET.get('page')
    try:
        contacts = pageinator.page(page)
    except PageNotAnInteger:
        # ���page����������ȡ��һҳ����
        contacts = pageinator.page(1)
    except EmptyPage:
        # ���page���ڷ�Χ�ڣ�ȡ���һҳ����
        contacts = pageinator.page(pageinator.num_pages)

    return render(request, "event_manage.html", {"user": username,
                                                 "events": contacts,
                                                 "name": search_name})


# �α�����
@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()
    # ��ҳ
    pageinator = Paginator(guest_list, 2)
    page = request.GET.get('page')
    try:
        contacts = pageinator.page(page)
    except PageNotAnInteger:
        # ���page����������ȡ��һҳ����
        contacts = pageinator.page(1)
    except EmptyPage:
        # ���page���ڷ�Χ�ڣ�ȡ���һҳ����
        contacts = pageinator.page(pageinator.num_pages)

    return render(request, "guest_manage.html", {"user": username,
                                                 "guests": contacts})


# �α��ֻ�������
@login_required
def search_phone(request):
    username = request.session.get('user', '')
    search_phone = request.GET.get("phone", '')
    search_name_bytes = search_phone.encode(encoding="utf-8")
    guest_list = Guest.objects.filter(phone__contains=search_name_bytes)
    # ��ҳ
    pageinator = Paginator(guest_list, 2)
    page = request.GET.get('page')
    try:
        contacts = pageinator.page(page)
    except PageNotAnInteger:
        # ���page����������ȡ��һҳ����
        contacts = pageinator.page(1)
    except EmptyPage:
        # ���page���ڷ�Χ�ڣ�ȡ���һҳ����
        contacts = pageinator.page(pageinator.num_pages)
    return render(request, "guest_manage.html", {"user": username,
                                                 "guests": contacts,
                                                 "phone": search_phone})


# ǩ��
@login_required
def sign_index(request, eid):
    event = get_object_or_404(Event, id=eid)
    return render(request, 'sign_index.html', {'event': event})


# ǩ������
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


# �˳���¼
@login_required
def logout(request):
    auth.logout(request)
    response = HttpResponseRedirect('/index/')
    return response
