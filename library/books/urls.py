from django.contrib import admin
from django.conf.urls import url

urlpatterns = [
    # API to borrow a book
    url('/borrowBooks', BorrowBook.as_view(), name="borrowBook"),

    # API to get the books borrowed by a user
    url('/getBooksBorrowed/<customer_id>/', GetBooksBorrowed.as_view(), name="getBooksBorrowed"),

    # API to add a book to the library
    url('/addBooks', AddBooks.as_view(), name="addBook"),

    # Get All books
    url('/getAllBooks', GetAllBooks.as_view(), name="getAllBook"),

    # Get the details of a book
    url('/getBookDetails/<book_id>', GetBookDetails.as_view(), name="getBookDetails"),
]

