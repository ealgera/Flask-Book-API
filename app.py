import datetime
import json

import jwt
from flask import Flask, Response, jsonify, request

from BookModel import *
from settings import *

app.config["SECRET_KEY"] = "test123"
# books = [
#    {
#        "name": "Green Eggs and Ham",
#        "price": 7.99,
#        "isbn": 978039400165
#    },
#    {
#        "name": "The Cat in the Hat",
#        "price": 6.99,
#        "isbn": 9782371000193
#    }
# ]


def validBookObject(bookObject):
    if "name" in bookObject and "price" in bookObject and "isbn" in bookObject:
        return True
    else:
        return False


def validBookUpdateObject(bookObject):
    if "name" in bookObject and "price" in bookObject:
        return True
    else:
        return False


@app.route("/login")
def get_token():
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
    token = jwt.encode(
        {"exp": expiration_date}, app.config["SECRET_KEY"], algorithm="HS256"
    )
    return token


# GET /books
@app.route("/books")
def get_books():
    token = request.args.get("token")
    try:
        jwt.decode(token, app.config["SECRET_KEY"])
    except:
        return jsonify({"error": "Need a valid token to view this page"}), 401
    return jsonify({"books": Book.get_all_books()})


# GET /books/ISBN NUMBER
@app.route("/books/<int:isbn>")
def get_books_by_isbn(isbn):
    return_value = Book.get_book(isbn)
    # return_value = {}
    # for book in books:
    #    if book["isbn"] == int(isbn):
    #        return_value = {
    #            "name": book["name"],
    #            "price": book["price"]
    #        }
    return jsonify(return_value)


# POST /books
# {
# 	"name": "Frankenstein"
# 	"price": 7.99
# 	"isbn": 123123123123
# }


@app.route("/books", methods=["POST"])
def add_book():
    request_data = request.get_json()
    if validBookObject(request_data):
        # newBook = {
        #    "name": request_data["name"],
        #    "price": request_data["price"],
        #    "isbn": request_data["isbn"]
        # }
        # books.insert(0, newBook)
        Book.add_book(request_data["name"], request_data["price"], request_data["isbn"])
        response = Response("", status=201, mimetype="application/json")
        # Location header stuurt de client naar een vervolg-pagina, in dit geval het zojuist
        # gecreerde "book"
        response.headers["Location"] = "/books/" + str(request_data["isbn"])
    else:
        invalidBookObject = {
            "error": "Invalid book object passed in request",
            "helpString": "Valid data: {'name': 'bookname', 'price': 9.99, 'isbn': 978012345}",
        }
        response = Response(
            json.dumps(invalidBookObject), status=400, mimetype="application/json"
        )
    return response


# PUT /books/978012345
# {
#    "name": "New name"
#    "price": <new price>
# }
@app.route("/books/<isbn>", methods=["PUT"])
def replace_book(isbn):
    request_data = request.get_json()
    if not validBookUpdateObject(request_data):
        invalidBookObjectErrorMsg = {
            "error": "Invalid book object passed in request",
            "helpString": "Valid data: {'name': 'bookname', 'price': 9.99, 'isbn': 978012345}",
        }
        response = Response(
            json.dumps(invalidBookObjectErrorMsg),
            status=400,
            mimetype="application/json",
        )
        return response
    Book.replace_book(isbn, request_data["name"], request_data["price"])
    #   new_book = {
    #       "name": request_data["name"],
    #       "price": request_data["price"],
    #       "isbn": int(isbn)
    #   }
    #   for i, book in enumerate(books):
    #       if book["isbn"] == int(isbn):
    #           books[i] = new_book
    #           break
    #       else:
    #           print(f"Boek niet gevonden ({isbn})")
    response = Response("", status=204)  # , mimetype="application/json")
    return response


# PATCH /books/<ISBN NUMBER>
# {
#    "name": "<new book name>"
# }
#
# or
#
# {
#    "price": <new price>
# }
@app.route("/books/<isbn>", methods=["PATCH"])
def update_book(isbn):
    request_data = request.get_json()
    # updated_book = {}
    if "name" in request_data:
        #        updated_book["name"] = request_data["name"]
        Book.update_book_name(isbn, request_data["name"])
    if "price" in request_data:
        #       updated_book["price"] = request_data["price"]
        Book.update_book_price(isbn, request_data["price"])
    #   for book in books:
    #       if book["isbn"] == int(isbn):
    #           book.update(updated_book)  # Unchanged if no values in updated_book
    response = Response("", status=204)
    response.headers["Location"] = "/books/" + str(isbn)
    return response


# DELETE /books/<ISBN NUMBER>
@app.route("/books/<isbn>", methods=["DELETE"])
def delete_book(isbn):
    #    for i, book in enumerate(books):
    #        if book["isbn"] == int(isbn):
    #            books.pop(i)
    #            return (Response("", status=204))
    if Book.delete_book(isbn):
        response = Response("", status=204)
        return response
    error = f"Book with ISBN {isbn} not found, nothing deleted."
    bookNotFoundErrorMsg = {"error": error}
    return Response(
        json.dumps(bookNotFoundErrorMsg), status=404, mimetype="application/json"
    )


app.run(port=5000)
