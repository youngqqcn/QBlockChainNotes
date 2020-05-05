from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import Book


class HelloCBV(View):

    def get(self, request):
        return HttpResponse("hello cbv")





class BooksAPI(View):

    def get(self, request):
        books = Book.objects.filter().all()

        # booklist = books.values_list()
        # print(booklist)
        print(books)
        booklist = [book.to_dict() for book in books]

        data = {
            'status': 200,
            'msg': 'ok',
            'data': booklist
        }

        return JsonResponse(data=data)
        pass

    def post(self, request):
        book_name = request.POST.get('book_name')
        book_price = request.POST.get('book_price')

        print(book_name)
        print(book_price)

        # book = Book( **{'name' : book_name, 'price' : book_price} )
        # book = Book(name=book_name, price = book_price)
        book = Book()
        book.name = book_name
        book.price = book_price

        book.save()

        rspdata = {
            'status': 201,
            'msg': 'create sucess',
            'data': book.to_dict()
        }

        return JsonResponse(data=rspdata)
        pass

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(BooksAPI, self).dispatch(*args, **kwargs)




class BookAPI(View):
    def get(self, request, bookid : int):
        book = Book.objects.get(pk=bookid)

        rspdata = {
            'status': 204,
            'msg': 'create sucess',
            'data': book.to_dict()
        }
        return JsonResponse(data=rspdata, status=204)
        pass

    def post(self, request, bookid : int):
        book_id = bookid
        book_name = request.POST.get('book_name')
        book_price = request.POST.get('book_price')

        print(book_name)
        print(book_price)

        # book = Book( **{'name' : book_name, 'price' : book_price} )
        # book = Book(name=book_name, price = book_price)
        book = Book()
        book.id = bookid
        book.name = book_name
        book.price = book_price

        book.save()

        rspdata = {
            'status': 201,
            'msg': 'create sucess',
            'data': book.to_dict()
        }

        return JsonResponse(data=rspdata)


    def delete(self, request, bookid : int):

        book = Book.objects.get(pk=bookid)
        if book:
            book.delete()
            rspdata = {
                'status': 200,
                'msg': 'book delete sucess',
                'data': {}
            }
            return JsonResponse(data=rspdata, status=200)
        else:
            rspdata = {
                'status': 404,
                'msg': 'book not exist',
                'data': {}
            }
            return JsonResponse(data=rspdata, status=404)

