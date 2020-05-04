from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import Book


@csrf_exempt
def books(request):
    if request.method  == 'GET':

        books = Book.objects.filter().all()

        # booklist = books.values_list()
        # print(booklist)
        print(books)
        booklist = [ book.to_dict()  for book in books  ]

        data = {
            'status' : 200,
            'msg' : 'ok',
            'data' : booklist
        }

        return JsonResponse(data= data)

    elif request.method == 'POST':
    #
    #     print(request.POST.keys())
    #     book_name = request.GET.get('book_name')
    #     book_price = request.GET.get('book_price')

        # request.GET.dict()
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
            'status' : 201,
            'msg' : 'create sucess',
            'data' : book.to_dict()
        }

        return JsonResponse(data=rspdata)


@csrf_exempt
def book(request, bookid : int):

    if request.method == 'GET':

        book  = Book.objects.get(pk=bookid)

        rspdata = {
            'status': 204,
            'msg': 'create sucess',
            'data': book.to_dict()
        }
        return JsonResponse(data=rspdata, status=204)

    elif request.method == 'POST':
        pass
    elif request.method == 'DELETE':

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
            return JsonResponse(data=rspdata, status= 404)

