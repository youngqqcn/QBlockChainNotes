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



class Students(models.Model):
    sname = models.CharField(max_length=20)
    sgender = models.BooleanField(default=True)
    sage = models.IntegerField()
    scontend = models.CharField(max_length=20)
    is_delete = models.BooleanField(default=False)


    sgrade = models.ForeignKey(Grades, on_delete=models.CASCADE)  #联级删除

    # def __str__(self):
    #     return self.sname





