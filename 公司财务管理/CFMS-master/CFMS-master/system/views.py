from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import redirect
from django.template import RequestContext
from django.contrib.auth import authenticate
from . import forms
from .models import User, Accounting_subjects,Accounting_subjects_new,Journal,ConfirmString
import datetime
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import hashlib
import random

#主页
def index(request):
    pass
    return render(request,'index.html')

#登录
def login(request):
    if request.session.get('is_login',None):
        return redirect("/index/")
    if request.method == "POST":
        #当数据请求中没有username键时不会抛出异常，而是返回一个我们制定的默认值None
        login_form = forms.UserForm(request.POST)
        message = '所有字段都必须填写！'
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(company_name=username)
                if not user.has_confirmed:
                    message = "该用户还未通过邮件确认！"
                    return render(request),'login.html',locals()
                if user.password == hash_code(password):
                    #往session字典内写入用户状态和数据
                    request.session['is_login'] = True
                    request.session['user_id'] = user.company_ID
                    request.session['user_name'] = user.company_name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = '用户不存在！'
        #locals是Python内置函数，它返回当前所有的本地变量字典
        return render(request, 'login.html', locals())
    #对于GET方法返回空表单让用户填写数据
    login_form=forms.UserForm()
    return render(request, 'login.html', locals())

#哈希函数
def hash_code(s, salt='CFMS'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()

#创建确认码对象的函数
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.company_name, now)
    ConfirmString.objects.create(code=code, user=user, c_time=now)
    return code

#发送邮件函数
def send_email(email, code):

    subject = '来自cfms_nju的注册确认邮件'
    text_content = '''感谢注册本系统，期待我们共同交流，共同进步！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''
    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>邮箱验证</a></p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

#处理邮箱验证函数
def user_register_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'confirm.html', locals())
    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
        return render(request, 'confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return render(request, 'confirm.html', locals())

#注册
def register(request):
    # 如果当前处于登录状态，则不允许注册
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        # 获取数据
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            if password1 != password2:
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                same_name_user = User.objects.filter(company_name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'register.html', locals())
                # 无特殊情况，创建新用户
                new_user = User()
                new_user.company_ID = random.randint(0,1000000)
                new_user.company_name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.save()
                code = make_confirm_string(new_user)
                send_email(email, code)
                message = '请前往注册邮箱，进行邮件确认'
                return render(request, 'confirm.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'register.html', locals())

#登出
def logout(request):
    if not request.session.get('is_login',None):
        #如果本来就没有登录，也就没有登出一说
        return redirect('/index/')
    request.session.flush()
    return redirect("/index/")

#录入日记账
def Journalizing(request):
    return render(request,'journal.html')
