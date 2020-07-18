# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Book(models.Model):
    # Name of the book
    name = models.CharField(max_length=64, default="random-book")

    # Author of the book
    author = models.CharField(max_length=64, null=True, blank=True)

    # Description about the book
    description = models.CharField(max_lenth=264, null=True, blank=True)

    # No of this book
    book_count = models.PositiveIntegerField(default=0)


class Customer(models.Model):
    # Name of the customer
    name = models.CharField(max_length=64, default="")

    # User
    user = models.ForegnKey(User)

    # Number of books borrowed
    books_count = models.PositveIntegerField(default=0)


class CustomerBook(models.Model):

    # Book which the customer borrowed
    book = models.ForeignKey(Book, null=True)

    # Customer
    customer = models.ForeignKey(Customer, null=True)

    # Date which the book is borrowed
    borrowed_date = models.DateTimeField(null=True)
