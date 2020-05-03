from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from .models import Grades, Students, StudentsManager
from django.db.models import Max, Min, Sum, Avg

def index(request):
    return HttpResponse("Hello, world. this is index page")


def detail(request, num):
    return HttpResponse(f"this is page {num}")


def grades_details(request):
    #去modles取数据
    grades = Grades.objects.all()

    return  render(request, "myApp/grades.html", {
        "grades" : grades
    })


def get_grade_students(request, grade_id : int):
    """
    展示一个班级的所有学生
    :param request:
    :param grade_id:
    :return:
    """

    grade = Grades.objects.get(id=grade_id)
    all_students = grade.students_set.all()
    return  render(request=request,
                   template_name="myApp/students.html",
                   context={
                       "students" : all_students
                   })



def students_details(request):

    # students = Students.objects.all()
    students = Students.stu_not_delete.all()
    return  render(request=request,
                   template_name="myApp/students.html" ,
                   context={
                       "students" : students
                   })

def add_default_student(request):

    grade = Grades.objects.get(id=1)


    #使用模型类
    stu = Students.create_student(name='default',
                                  age=999,
                                  gender=False,
                                  contend='this is default',
                                  grade=grade,
                                  is_delete=False)

    stu.save()
    return HttpResponse(content='added successed')



def add_default_student_use_manager(request):

    grade = Grades.objects.get(id=1)

    #使用自定义管理器
    stu = Students.create_student(name='default2',
                                  age=999,
                                  gender=False,
                                  contend='this is default2',
                                  grade=grade,
                                  is_delete=False)
    stu.save()
    return HttpResponse(content='added successed')

def show_students_page(request, page_index :  int):

    assert page_index >= 1

    page_size = 2

    stus =  Students.stu_not_delete.all()[(page_index - 1) * page_size : page_index * page_size]
    return render(request=request,
                template_name="myApp/students.html",
                  context={
                      "students" : stus
                  })


def search_student(request):
    #模糊查询
    # stus = Students.stu_not_delete.filter(sname__contains='t')
    # stus = Students.stu_not_delete.filter(sage__gte=20) #年龄大于等于20

    max_age = Students.stu_not_delete.aggregate(Max('sage'))

    print(max_age)


    stus = []

    return render(request=request,
                  template_name="myApp/students.html",
                  context={
                      "students": stus
                  })


def search_relate(request):

    #关联查询:  查询scontend中包含 'hapy' 的学生属于哪些班级
    grades = Grades.objects.filter(students__scontend__contains='hapy')
    print(len(grades))
    return render(request, "myApp/grades.html", {
        "grades": grades
    })


from django.db.models import F,  Q
def search_student_by_F(request):

    grades = Grades.objects.filter(ggirlnum__gt=F("gboynum"))
    print(grades)
    return  HttpResponse(f"found {len(grades)}")


def search_student_by_Q(request):
    #  Q(xx) | Q(xxx)  或
    #  Q(xx) &  Q(xxx) 且
    # ~Q(xxxx)   非
    students = Students.stu_not_delete.filter( ~( Q(sgender=False)  & Q(sage__lt=30) ) )
    return render(request=request,
              template_name="myApp/students.html",
              context={
                  "students": students
              })


def  test_re_path(request):
    return HttpResponse("ok")


import json

def request_props(request):
    rsp = {
        'path': request.path,
        'method': request.method,
        'encoding': request.encoding,
        'GET' : request.GET,
        'POST' : request.POST,
        'FILES' : request.FILES,
        'COOKIES' : request.COOKIES,
        'session' : request.session.is_empty(),
        'is_ajax' : request.is_ajax()
    }

    return HttpResponse( json.dumps(rsp) )


def  get_url_parameters(request):

    rsp = request.GET
    return HttpResponse( json.dumps(rsp) )



def  get_url_parameters2(request):

    #  http://127.0.0.1:8000/get2?a=999,444&b=222&c=ccccc
    a = request.GET.getlist('a')
    print(type(a))
    return HttpResponse( json.dumps(a) )


def show_register(request):
    return render(request=request, template_name="myApp/register.html")

def register(request):

    name = request.POST.get("name")
    hobby = request.POST.get("hobby")
    gender = request.POST.get("gender")

    rsp = {
        "name" : name,
        "hobby" : hobby,
        "gender" : gender,
    }

    return  HttpResponse(json.dumps(rsp))


def show_response(request):

    # rsp = HttpResponse(content='xxxxxx')
    # rsp.write()
    # rsp.set_cookie()
    # rsp.get()
    # rsp.getvalue()
    # rsp.close()
    # rsp.serialize()
    # rsp.delete_cookie()
    # rsp.set_signed_cookie()
    return HttpResponse('')


# 设置了cookie 之后, 以后的每次请求都会带上  cookie
def set_custom_cookies(request):
    rsp = HttpResponse()
    rsp.set_cookie("MYCOOKIE", "THIS IS MY COOIKES")
    return rsp


from django.http import HttpResponseRedirect

def test_redirect(request):

    # 重定向到 子路径下的 request_props
    # return HttpResponseRedirect(redirect_to='request_props/')

    #重定向到根路径下的
    return HttpResponseRedirect(redirect_to='/request_props/')


from django.http import JsonResponse
def json_response(request):


    data = {
        'name' : 'yqq',
        'age' : 10,
        'hobby' : 'music'
    }

    return  JsonResponse(data=data)


# path(r'mainpage/', views.show_main_page, name='show_main_page'),
#     path(r'user_login/', views.user_login, name='login')

def show_main_page(request):

    #为什么默认值没有生效????
    username = request.session.get('username', default="游客")

    if username is None: username = "游客"
    return  render(request=request,
                   template_name="myApp/mainpage.html",
                   context={
                       'username' : username
                   })

def show_login_page(request):
    return render(request=request,
                  template_name="myApp/login.html")



#在django_session 表中  的 session_data有 username, base64编码

def user_login(request):

    username = request.POST.get('username')
    request.session['username'] =username

    request.session.set_expiry(value=1000) #10s过期


    return  HttpResponseRedirect('/mainpage/')
    pass


from django.contrib.auth import login, logout
def user_logout(request):
    # request.session.delete('username')  #行不通
    # logout(request)

    # request.session.clear()  #ok
    # request.session.flush() #ok
    logout(request)  #推荐

    return HttpResponseRedirect('/mainpage/')


def students_counter(request):

    stus = Students.stu_all.all()

    strtmp = "this is test string"

    return render(request=request, template_name="myApp/students_counter.html"
           ,context={
            "students" : stus,
            "strtmp" : strtmp
        })



def show_reverse_url_page(request):
    return  render(request=request,
                   template_name="myApp/reverse_mapping_url.html",
                   )

def reverse_url_test(request, num : int):

    return HttpResponse(content=f"test successed!  num is {num}")

def template_externs(request):
    return render(request=request, template_name="myApp/sub_page.html")



def html_code(request):
    return render(request=request,
                  template_name="myApp/html_code.html",
                  context={
                      'html_rsp' : "<h1>This is html h1!</h1>"
                  })


def show_test_csrf_page(request):
    return render(request=request,
                  template_name='myApp/csrf_test.html' )




def verifycode(request):
    # 引入绘图模块
    from PIL import Image, ImageDraw, ImageFont
    # 引入随机函数模块
    import random
    # 定义变量，用于画面的背景色，宽，高
    bgcolor = (random.randrange(20, 100), random.randrange(20, 100), random.randrange(20, 100))
    width = 100
    height = 50
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画面对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    characters = '1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += characters[random.randrange(0, len(characters))]
    # 构造字体对象
    font = ImageFont.truetype(r'C:\Windows\Fonts\Arial.ttf', 40)
    # 构造字体颜色
    fontcolor1 = (255, random.randrange(0, 255), random.randrange(0, 255))
    fontcolor2 = (255, random.randrange(0, 255), random.randrange(0, 255))
    fontcolor3 = (255, random.randrange(0, 255), random.randrange(0, 255))
    fontcolor4 = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor1)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor2)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor3)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor4)
    # 释放画笔
    del draw

    # 存入session,用于做进一步的验证
    request.session['verifycode'] = rand_str


    # 内存文件操作
    import io
    buf = io.BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


def verify_code_image(request):
    return verifycode(request)




def test_csrf(request):

    # print(request.POST)
    right_verifycode = request.session.get('verifycode')
    user_post_verifycode = request.POST.get('verifycode')

    if right_verifycode.upper() != user_post_verifycode.upper():
        return redirect(to="/show_test_csrf_page/")

    username = request.POST.get("username")
    password = request.POST.get("passwd")

    return  HttpResponse("登录成功!!" + json.dumps(
        {
            'username' : username,
            'password' : password,
        }
    ))



def static_page(request):

    return render(request=request,
                  template_name="myApp/my_static.html")



def upload_file_page(request):
    return render(request=request,
                  template_name="myApp/upload_file.html")


import os
from django.conf import settings

def upload_file(request):

    if request.method != 'POST':
        return HttpResponse('failed!')

    # file = request.FILES["file"]
    file = request.FILES.get("file")
    file_path = os.path.join( settings.MEDIA_ROOT, file.name)

    with open(file_path, 'wb') as outfile:
        for block in file.chunks():  #
            outfile.write(block)

    return HttpResponse("uploaded success!")


from django.core.paginator import Paginator
def  student_paginator(request, page_index : int):

    students = Students.stu_all.all()

    paginator = Paginator( object_list=students, per_page=2 )

    one_page_stus = paginator.get_page(number= page_index )

    return render(request=request,
                  template_name="myApp/student_paginator.html",
                  context={
                      "students" : one_page_stus
                  })


def test_ajax(request):

    all_stus = Students.stu_all.all()
    stus_list =  all_stus.values()
    print(stus_list)
    # print(type(stus_list))
    retdata = [ item for item in stus_list ]


    return JsonResponse({"data": retdata})
    # return JsonResponse({'name' : 'yqq'})

def show_test_ajax_page(request):
    return render(request=request,
                  template_name="myApp/test_ajax.html",
         )



def test_mctext(request):

    return render(request=request,
                  template_name='myApp/test_tinymce.html')



#
# # from .task import test_celery_task
# # from .task import
# # import myApp.task
# # from myApp import task
# from .task import TestCeleryTask
# def test_celery(request):
#
#     # test_celery_task()
#     # res = task.test_celery_task.delay(1, 3)
#     # TestCeleryTask.apply_async(args=('gooood',  ))
#     # print(f'result {res}')
#
#     return render(request=request,
#                   template_name='myApp/test_celery.html')