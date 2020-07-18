# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from books.models import *
from django.utils import timezone

# Create your views here.
class Register(View):
    def validate_post_data(self, jsonData):
        '''
        Function to validate the field names of the Json data provided from front end
        '''
        return (jsonData.has_key("name") and jsonData.has_key("email") and jsonData.has_key("password"))

    def valid_email_domain(self, email):
        '''
        Expecting the email in <NAME>@<DOMAIN>.com
        '''
        splitted_email = email.split("@")
        if splitted_email:
            domain = splitted_email[1].split(".")[0]
            if domain not in ["gmail", "yahoo", "outlook"]:
                return False

        return True

    def create_error_response(self, errString):
        resp = {}
        resp["status"] = "error"
        resp["errString"] = errString

        return resp


    def post(self, request):
        '''
        Expecting a data in JSON like {"name": <Name>, "email": <email>, "password": <password>}
        '''
        resp = {}
        try:
            jsonData = json.loads(request.body.decode("utf-8"))
        except:
            errString = "Empty JSON"
            return JsonResponse(self.create_error_response(errString), status=404)

        if not self.validate_post_data(jsonData):
            errString = "Invalid JSON fields provided"
            return JsonResponse(self.create_error_response(errString), status=401)

        if not self.valid_email_domain(jsonData["email"]):
            errString = "Invalid email domain provided"
            return JsonResponse(self.create_error_reponse(errString))

        try:
            customer = Customer.objects.get(user__email=jsonData["email"])
        except:
            # Creating a user object
            user = User.objects.create(username=jsonData["email"], email=jsonData["email"])
            user.first_name = jsonData["name"]
            user.set_password(jsonData["password"])
            user.save()

            # Creating a customer object
            customer = Customer.objects.create(name=jsonData["name"], user=user)
        else:
            errString = "User with given email id already exists"
            return JsonResponse(self.create_error_response(errString), status=400)

        resp["status"] = "success"
        resp["succString"] = "User created successfully"
        return JsonResponse(resp, status=200)

    # End of post
# End of Register

class Login(Register, View):

    def validate_post_data(self, jsonData):
        return (jsonData.has_key("email") and jsonData.has_key("password"))

    def post(selg, request):
        resp = {} # Return response in JSON format
        try:
            jsonData = json.loads(request.body.decode("utf-8"))
        except:
            errString = "Empty JSON"
            return JsonResponse(self.create_error_response(errString), status=404)

        if not self.validate_post_data(jsonData):
            errString = "Invalid Json Fields"
            return JsonResponse(self.create_error_response(errString), status=401)

        try:
            customer = Customer.objects.get(user__email=jsonData["email"])
        except:
            errString = "User with given email does not exists"
            return JsonResponse(self.create_error_response(errString), status=404)

        # Authenticating the user
        user = authenticate(username=jsonData['email'], password=jsonData["password"])

        if not user:
            errString = "Invalid credentials, Please check the password"
            return JsonResponse(self.create_error_response(errString), status=400)

        resp["staus"] = "Success"
        resp["succString"] = "User is authenticated successfuly"
        return JsonResponse(resp, status=200)

    # End of post
# End of Login

class BorrowBook(Register, View):

    def validate_post_data(self, jsonData):
        return (jsonData.has_key("book_id") and jsonData.has_key("date"))

    @method_decorator(login_required)
    def post(self, request):
        '''
        API to borrow a book for a Customer
        Expecting request will have {"book_id": <book id>, "date": <Date>}
        Need to create a Book Object with book id and date which the book is borrowed
        '''
        resp = {}
        try:
            jsonData = json.loads(request.body.decode("utf-8"))
        except:
            errString = "Empty JSON"
            return JsonResponse(self.create_error_response(errString), status=404)

        try:
            customer=Customer.objects.get(user_id=request.user.id)
        except:
            errString = "Not Authorized, User does not exists"
            return JsonResponse(self.create_error_response(errString), status=401)

        if not self.validate_post_date(jsonData):
            errString = "Invalid JSON fields in the JSON"
            return JsonResponse(self.create_error_response(errString), status=404)

        try:
            book = Book.objects.get_or_create(id=jsonData["book_id"])
        except:
            errString = "Book with given ID does not exists"
            return JsonResponse(self.create_error_response(errString, status=404))
        
        if book.book_count > 0:
            book.book_count -= 1
            book.save()
            
            customer.books_borrowed += 1
            customer.save()
            
            customerBook = CustomerBook()
            customerBook.customer = customer
            customerBook.book = book
            customerBook.borrowed_date = timezone.now()

        else:
            errString("Requested book is not available")
            return JsonResponse(self.create_error_response(errString), status=404)


        resp["status"] = "success"
        resp["succString"] = "A book object is successfully added"
        return JsonResponse(resp, status=200)

    # End of post
# End of BorrowBook

class GetBooksBorrowed(Register, View):

    @method_decorator(login_required)
    def get(self, request, customer_id):
        """
        API to get the books borrowed by a customer
        """
        resp={}
        try:
            customer = Customer.objects.get(id=customer_id)
        except:
            errString = "You are Unauthorized to access this API"
            return JsonResponse(errString, status=401)

        customerBooks = CustomerBook.objects.filter(customer = customer)

        resp["books"] = []
        if customerBooks.exists():
            for customerBook in customerBooks:
                each_book={}
                each_book["name"] = customerBook.book.name
                each_book["author"] = customerBook.book.author
                each_book["description"] = customerBook.book.description
                each_book["borrowed_date"] = customerBook.borrowed_date

                resp["books"].append(each_book)

        return JsonResponse(resp, status = 200)

class AddBooks(Register):

    def validate_post_date(jsonData):
        return jsonData.has_key("books"):

    @method_decorator(login_required)
    def post(self, request):
        """
        API to add a book to the library by the customer
        expecting a request like
        {"books": [{"book_name":<book_name>, "author":<book_author>, "bookCount":<book count>}, {}, {}, {}, ........]}
        """
        resp={}

        try:
            customer = Customer.objects.get(user__id=request.user.id)
        except:
            errString("Unauthorized User")
            return JsonResponse(self.create_error_response(errString), status=401)

        try:
            jsonData = json.loads(request.body.decode("utf-8"))
        except:
            errString = "Empty JSON"
            return (self.create_error_response(errString), status=404)

        if not self.validate_post_date(jsonData):
            errString = "Invalid data fields provided"
            return JsonResponse(self.create_error_response(errString), status=404)

        if jsonData["books"]:
            for each_book in jsonData["books"]:
                book = Book.objects.get_or_create(name=jsonData["name"], author=jsonData["author"])
                book.book_count += jsonData[bookCount]
                book.save()
        
        resp["status"] = "success"
        resp["succString"] = "Books are added successfully"

        return JsonResponse(resp, status=200)


class GetAllBooks(Register):
    @methor_decorator(login_required)
    def get(self, request):
        resp = {}
        
        try:
            customer = Customer.objects.get(user__id=request.user.id)
        except:
            errString = "Unauthorized User"
            return JsonResponse(self.create_error_response(errString), status=401)

        books = Book.objects.filter()
        resp["books"] = []
        for book in books:
            each_book = {}
            each_book["name"] = book.name
            each_book["author"] = book.author
            each_book["description"] = book.description
            each_book["books_available"] = book.books_count

            resp["books"].append(each_book)


        return JsonResponse(resp, status = 200)


class GetBookDetails(Register):

    @method_decorator(login_required)
    def get(self, request, book_id):

        resp = {}
        try:
            customer = Customer.objects.get(user__id=request.user.id)
        except:
            errString = "Unauthorized User"
            return (self.create_error_response(errString), staus=401)

        try:
            book = Book.objects.get(id=book_id)
        except:
            errString = "Book not found"
            return (self.create_error_response(errString), status=404)

        resp["bookName"] = book.name
        resp["author"] = book.author
        resp["description"] = book.description
        resp["books_available"] = book.books.count

        return JsonResponse(resp, status=200)
