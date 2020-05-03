from django.db import models

# Create your models here.


from django.db import models

class   Grades(models.Model):
    gname = models.CharField(max_length=20)
    gdate = models.DateTimeField()
    ggirlnum  = models.IntegerField()
    gboynum = models.IntegerField()
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.gname




class StudentsManager(models.Manager):

    def get_queryset(self):
        return super(StudentsManager, self).get_queryset().filter(is_delete=False)

    def create_student(self, name, age, gender, contend, grade, is_delete=False):
        stu = self.model()
        stu.sname = name
        stu.sage = age
        stu.sgender = gender
        stu.scontend = contend
        stu.sgrade = grade
        stu.is_delete = is_delete
        return stu




class Students(models.Model):

    sname = models.CharField(max_length=20)
    sgender = models.BooleanField(default=True)
    sage = models.IntegerField()
    scontend = models.CharField(max_length=20)
    is_delete = models.BooleanField(default=False)

    sgrade = models.ForeignKey(Grades, on_delete=models.CASCADE)  #联级删除


    stu_all = models.Manager()
    stu_not_delete = StudentsManager()  #自定义管理器

    def __str__(self):
        return self.sname


    class Meta:
        db_table = "myApp_students"
        ordering = ["id"]

    @classmethod
    def create_student(cls, name, age, gender, contend, grade, is_delete=False):
        stu = cls(sname=name, sage=age, sgender=gender, scontend=contend,
                  sgrade=grade, is_delete=is_delete)
        return stu



from tinymce.models import HTMLField
class MCE_Text(models.Model):
    str = HTMLField()
