```
pip install djangorestframework
pip install markdown       # Markdown support for the browsable API.
pip install django-filter  # Filtering support

```


django-rest-framework

- 序列化器
- 视图函数
  - viewsets..ModelViewSet
  - CBV
  - 视图集合
- 路由
  - router.DefaultRouter
- 需要 INSTALLED_APPS中添加 `rest_framework`
- runserver
  - 所有API可视化
  - 超链接  HyperLinkedModelSerializer
  - 对数据集合实现了
    - 路由  user
    - get
    - post
  - 对单个数据实现了
    - get
    - post
    - put
    - delete
    - patch
  - viewsets 做了视图函数的实现
  - router 做了路由的注册

 