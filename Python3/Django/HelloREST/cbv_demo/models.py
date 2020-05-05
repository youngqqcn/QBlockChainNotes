from django.db import models

# Create your models here.


class Book(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=20, decimal_places=3)


    def keys(self):
        # return ('pk', 'name', 'price') #ok
        return ('id', 'name', 'price')  #ok

    def __getitem__(self, item):
        return getattr(self, item)


    def __str__(self):
        return  str(dict(self))

    def to_dict(self):
        return dict(self)

