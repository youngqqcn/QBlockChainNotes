from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Grades, Students


# admin.register(Grades)  #error
# admin.register(Students)  #error




#
class StudentsInfo(admin.TabularInline):  #admin.StackedInline

    model = Students
    extra = 2
    pass


@admin.register(Grades)
class GradesAdmin(admin.ModelAdmin):
    inlines = [StudentsInfo]

    # # 列表页属性
    # list_display = []  # 显示字段设置
    # list_filter = []  # 过滤字段设置
    # search_fields = []  # 搜索字段设置
    # list_per_page = []  # 分页设置


    # # 添加，修改页属性
    # fields = []  # 规定属性的先后顺序
    # fieldsets = []  # 给属性分组 注意：fields与fieldsets不能同时使用

    #
    list_display = ['pk', 'gname', 'gdate', 'ggirlnum', 'gboynum', 'is_delete']
    list_filter = ['gname']   #过滤字段
    search_fields = ['gname']
    # list_per_page = 5
    # fields = ['ggirlnum', 'gboynum', 'gname', 'gdate', 'is_delete']
    fieldsets = [
                    ("num",{"fields":['ggirlnum', 'gboynum']}),
                    ("base", {"fields":["gname", "gdate", "is_delete"]}),
    ]


@admin.register(Students)    #使用装饰器进行注册
class StudentAdmin(admin.ModelAdmin):


    #修改列表头
    def stu_gender(self):
        if self.sgender:
            return "男"
        else:
            return "女"

    stu_gender.short_description = "性别"

    list_display = ['pk', 'sname', 'sage', stu_gender, 'scontend', 'sgrade', 'is_delete']
    list_per_page = 2


    #执行动作在页面的位置
    actions_on_bottom = True
    actions_on_top = False

    pass


# admin.site.register(Students, StudentAdmin)
# admin.site.register(Grades, GradesAdmin)

from .models import MCE_Text
admin.site.register(MCE_Text)
