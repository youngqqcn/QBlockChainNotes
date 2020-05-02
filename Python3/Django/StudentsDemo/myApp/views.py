from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Grades, Students

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

    students = Students.objects.all()
    return  render(request=request,
                   template_name="myApp/students.html" ,
                   context={
                       "students" : students
                   })