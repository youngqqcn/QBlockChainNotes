from django.shortcuts import render

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
