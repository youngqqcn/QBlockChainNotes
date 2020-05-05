from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from .models import Book


def index(request):
    return JsonResponse(data={'data' : 'success'})




#http://127.0.0.1:8000/app/booklist/
class HelloListView(ListView):
    template_name = 'app/boolist.html'
    # paginator_class = Paginator()
    model = Book


    # template_engine = None
    # response_class = TemplateResponse
    # content_type = None
