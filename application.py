import os
from flask_sqlalchemy import SQLAlchemy
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, usd


# Configure application
app = Flask(__name__)
app.secret_key=os.environ.get('SECRET')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Configure CS50 Library to use SQLite database
app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL')

db.SQLAlchemy(app)

@app.route("/")
def index():
    """Render App Animation for 4secs"""

    return redirect("/login")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = :email",
                          email=request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/main")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("We will be waiting for you!")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        flash("One step closer to be our user!")
        return render_template("register.html")
    else:
        """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Getting the info from username input
        email = request.form.get("email")

        # Checking user typed in email input
        if not email:
            return apology("You must provide a username.", 403)

        # Getting the info from password and confirmation inputs
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Checking if they are exist and they have the same value or not
        if not password:
            return apology("You must provide a password.", 403)
        elif password != confirmation or not confirmation:
            return apology("Confirmation must be the same with your password!", 403)

        # Generating a hash code for password
        hashed = generate_password_hash(password)

        # Getting username from the input
        username = request.form.get("username")


        # Getting all the emails from the database
        emailList = db.execute("SELECT email FROM users")

        for mail in emailList:
            if email == mail["email"]:
                return apology("Email already exists!" , 403)

        # Addition of email and password to the database
        db.execute("INSERT INTO users (email, hash, username) VALUES (:email, :password, :username)",
            email=email, password=generate_password_hash(password), username=username)

        flash("Successfully Registered")
        return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method =="GET":
        # Get the tasks for TODO APP
        todoList = db.execute("SELECT task FROM todo WHERE id=:uid", uid=session["user_id"])
        # Get the username from the database
        userList = db.execute("SELECT username,email FROM users WHERE id=:uid", uid=session["user_id"])

        return render_template("profile.html", userList=userList, iD=session["user_id"], todoList=todoList)




@app.route("/info-change", methods=["GET", "POST"])
@login_required
def infoChange():
    """Change of userInfo"""
    if request.method=="POST":

        # Get values from the form
        email = request.form.get("email")
        username = request.form.get("username")

        # Check if they exist
        if not email:
            return apology("Give us an email address", 403)

        if not username:
            return apology("Give us a username", 403)

        # Update the database with the new values
        db.execute("UPDATE users SET email=:email, username=:user WHERE id=:uid", email=email, user=username, uid=session["user_id"])

        flash("User Info Changed!")
        return redirect("/profile")

@app.route("/pass-change", methods=["GET", "POST"])
@login_required
def passChange():
    """Change of password"""
    if request.method=="POST":

        # Get values from the form
        password = request.form.get("password")
        confirmation=request.form.get("confirmation")

        # Get the hash from database to check
        passwordList = db.execute("SELECT hash FROM users WHERE id=:uid" ,uid=session["user_id"])

        if passwordList:
            passwordDB = passwordList[0]["hash"]

            # Check if the password is already in use
            if check_password_hash(passwordDB, password):
                return apology("Password is already in use")

        # Check if the input is empty or not matching confirmation
        if not password:
            return apology("Give us a password", 403)
        elif not confirmation:
            return apology("You should type confirmation", 403)

        if password != confirmation:
            return apology("Must be the same!", 403)
        else:
            # UPDATE the database
            db.execute("UPDATE users SET hash=:password WHERE id=:uid", password=generate_password_hash(password), uid=session["user_id"])

            flash("Password changed!")
            return redirect("/profile")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method =="GET":
        # Get the tasks for TODO APP
        todoList = db.execute("SELECT task FROM todo WHERE id=:uid", uid=session["user_id"])
        # Get the username from the database
        userList = db.execute("SELECT username,email FROM users WHERE id=:uid", uid=session["user_id"])
        # Select for the Summary
        wholeList = db.execute("SELECT * FROM datetime WHERE id=:uid ORDER BY localtime DESC LIMIT 1", uid=session["user_id"])

        return render_template("add.html", userList=userList, iD=session["user_id"], wholeList=wholeList, todoList=todoList)

    else:

        # Get the dropdown value from the form
        dropDown = request.form.get("category")
        print(type(dropDown))

        # Get other form values
        # Book
        usageB = request.form.get("bUsage")
        nameB = request.form.get("bName")
        writer = request.form.get("writer")
        priceB = request.form.get("bPrice")
        quantityB = request.form.get("bQuantity")

        # Check the value of dropDown
        if dropDown == "books":
            # Select all the books for a check
            bookList = db.execute("SELECT * FROM books WHERE id=:uid", uid=session["user_id"])
            # If the book already exists
            if bookList:
                for books in bookList:
                    # If tha name of the book and its writer is the same with the one user has
                    if books["name"] == nameB and books["writer"] == writer and books["usage"] == usageB:
                        db.execute("UPDATE books SET quantity=quantity + :q WHERE id=:uid AND name=:n",
                            q=int(quantityB), uid=session["user_id"], n=nameB)

                        # Record the datetime
                        db.execute("INSERT INTO datetime (id, name, producer, price, usage, quantity, localtime) VALUES (:uid,:name, :pro, :pri, :u, :q, datetime('now','localtime'))",
                            uid=session["user_id"], name=nameB, pro=writer, pri=float(priceB), u=usageB, q=int(quantityB))

                        # Select for the Summary
                        wholeList = db.execute("SELECT * FROM datetime WHERE id=:uid ORDER BY localtime DESC LIMIT 1", uid=session["user_id"])

                        flash("Amount of existing book increased!")
                        return render_template("add.html", wholeList=wholeList)

            # Add the book values to the database
            db.execute("INSERT INTO books (id, name, writer, price, usage, quantity) VALUES (:uid, :name, :writer, :price, :usage, :q)",
               uid=session["user_id"], name=nameB, writer=writer, price=float(priceB), usage=usageB, q=int(quantityB))

            # Record the datetime
            db.execute("INSERT INTO datetime (id, name, producer, price, usage, quantity, localtime) VALUES (:uid,:name, :pro, :pri, :u, :q, datetime('now','localtime'))",
                uid=session["user_id"], name=nameB, pro=writer, pri=float(priceB), u=usageB, q=int(quantityB))

            # Select for the Summary
            wholeList = db.execute("SELECT * FROM datetime WHERE id=:uid ORDER BY localtime DESC LIMIT 1", uid=session["user_id"])

            flash("New Book Added!")
            return render_template("add.html", wholeList=wholeList)

        elif dropDown == "items":
             # Items
            usageI = request.form.get("iUsage")
            nameI = request.form.get("iName")
            producer = request.form.get("producer")
            priceI = request.form.get("iPrice")
            quantityI = request.form.get("iQuantity")

            # Select all the books for a check
            itemList = db.execute("SELECT * FROM items WHERE id=:uid", uid=session["user_id"])
            # If the book already exists
            if itemList:
                for items in itemList:
                    # If tha name of the book and its writer is the same with the one user has
                    if items["name"] == nameI and items["producer"] == producer and items["usage"] == usageI:
                        db.execute("UPDATE items SET quantity=quantity + :q WHERE id=:uid AND name=:n",
                            q=int(quantityI), uid=session["user_id"], n=nameI)

                        # Record the datetime
                        db.execute("INSERT INTO datetime (id, name, producer, price, usage, quantity, localtime) VALUES (:uid,:name, :pro, :pri, :u, :q, datetime('now','localtime'))",
                            uid=session["user_id"], name=nameI, pro=producer, pri=float(priceI), u=usageI, q=int(quantityI))

                        # Select for the Summary
                        wholeList = db.execute("SELECT * FROM datetime WHERE id=:uid ORDER BY localtime DESC LIMIT 1", uid=session["user_id"])

                        flash("Amount of existing book increased!")
                        return render_template("add.html", wholeList=wholeList)

            # Add the item values to the database
            db.execute("INSERT INTO items (id, name, producer, price, usage, quantity) VALUES (:uid, :name, :producer, :price, :usage, :q)",
               uid=session["user_id"], name=nameI, producer=producer, price=float(priceI), usage=usageI, q=int(quantityI))

            # Record the datetime
            db.execute("INSERT INTO datetime (id, name, producer, price, usage, quantity, localtime) VALUES (:uid,:name, :pro, :pri, :u, :q, datetime('now','localtime'))",
                uid=session["user_id"], name=nameI, pro=producer, pri=float(priceI), u=usageI, q=int(quantityI))

            # Select for the Summary
            wholeList = db.execute("SELECT * FROM datetime WHERE id=:uid ORDER BY localtime DESC LIMIT 1", uid=session["user_id"])

            flash("New Item added!")
            return render_template("add.html", wholeList=wholeList)

        else:
            return apology("Choose a category")


@app.route("/todo", methods=["GET", "POST"])
@login_required
def todo():
    if request.method=="POST":
        inputVal = request.form.get("newTodo")

        # INSERT IT TO DB
        db.execute("INSERT INTO todo (id, task, localtime) VALUES (:uid, :task, datetime('now','localtime'))",
            uid=session["user_id"], task=inputVal)

        # SELECT THE DATA FROM THE TABLE FOR PERMENANT RENDER
        todoList = db.execute("SELECT task FROM todo WHERE id=:uid", uid=session["user_id"])

        # Get the username from the database
        userList = db.execute("SELECT username,email FROM users WHERE id=:uid", uid=session["user_id"])

        # Select for the Summary
        wholeList = db.execute("SELECT * FROM datetime WHERE id=:uid ORDER BY localtime DESC LIMIT 1", uid=session["user_id"])

        return render_template("add.html", todoList=todoList, userList=userList, wholeList=wholeList)



@app.route("/main" , methods=["GET", "POST"])
@login_required
def main():
    if request.method == "GET":
        # Get the tasks for TODO APP
        todoList = db.execute("SELECT task FROM todo WHERE id=:uid", uid=session["user_id"])
        # Get the username from the database
        userList = db.execute("SELECT username,email FROM users WHERE id=:uid", uid=session["user_id"])

        # Get the collection list
        colist = db.execute("SELECT * FROM datetime WHERE id=:uid ORDER BY localtime DESC", uid=session["user_id"])

        # Get total expense, total amount of collection, total usage, total unused, total read, total unread
        collections = db.execute("SELECT SUM(price) as price, SUM(quantity) as quantity FROM datetime WHERE id=:uid", uid=session["user_id"])


        return render_template("main.html", userList=userList,colist=colist, collections=collections, iD=session["user_id"], todoList=todoList)


# Can be change into another function!
@app.route("/items")
@login_required
def items():
    ########################ITEMS#########################
    # Get the database info for unused items
    unusedTotal = db.execute("SELECT SUM(price*quantity) as price, SUM(quantity) as q FROM items WHERE id=:uid AND usage='unused'", uid=session["user_id"])
    itemsList = db.execute("SELECT * FROM items WHERE id=:uid AND usage='unused' ORDER BY name" , uid=session["user_id"])

    #checks
    if unusedTotal:
        unusedP = unusedTotal[0]["price"]
        unusedQ = unusedTotal[0]["q"]
    else:
        unusedP = 0.00
        unusedQ = ""

    # Get the database info for used items
    usedTotal = db.execute("SELECT SUM(price*quantity) as price, SUM(quantity) as q FROM items WHERE id=:uid AND usage='used'", uid=session["user_id"])
    usedList = db.execute("SELECT * FROM items WHERE id=:uid AND usage='used' ORDER BY name", uid=session["user_id"])

    # Checks
    if usedTotal:
        usedP = usedTotal[0]["price"]
        usedQ = usedTotal[0]["q"]
    else:
        usedP =0.00
        usedQ =""

    return render_template("items.html", unuseds=unusedTotal, itemsList=itemsList, usedList=usedList, unusedP=unusedP, unusedQ=unusedQ, usedP=usedP, usedQ=usedQ )

@app.route('/books')
@login_required
def books():
    ########################BOOKS#########################
    # Get the database info for unused items
    unreadTotal = db.execute("SELECT SUM(price*quantity) as price, SUM(quantity) as q FROM books WHERE id=:uid AND usage='unread'", uid=session["user_id"])
    booksList = db.execute("SELECT * FROM books WHERE id=:uid AND usage='unread' ORDER BY name" , uid=session["user_id"])

    #checks
    if unreadTotal:
        unreadP = unreadTotal[0]["price"]
        unreadQ = unreadTotal[0]["q"]
    else:
        unreadP = 0.00
        unreadQ = ""

    # Get the database info for used items
    readTotal = db.execute("SELECT SUM(price*quantity) as price, SUM(quantity) as q FROM books WHERE id=:uid AND usage='read'", uid=session["user_id"])
    readList = db.execute("SELECT * FROM books WHERE id=:uid AND usage='read' ORDER BY name", uid=session["user_id"])

    # Checks
    if readTotal:
        readP = readTotal[0]["price"]
        readQ = readTotal[0]["q"]
    else:
        readP =0.00
        readQ =""

    return render_template("books.html", booksList=booksList, readList=readList, unreadP=unreadP, unreadQ=unreadQ, readP=readP, readQ=readQ )


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    app.run()