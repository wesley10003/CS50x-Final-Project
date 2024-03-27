# Virtual Trading Platform
#### Video Demo:  <https://youtu.be/Md82_EbtHnY>
#### Description:

READ requirement.txt to see the essential modules

For my CS50 final project, I’ve decided to create a crypto trading platform using Python, flask, HTML, CSS, and JavaScript. The project is inspired by week 9’s problem set ‘finance.’ It was definitely my favourite problem throughout the CS50 course, as a result, I’ve decided to create something similar but add my own features to it to make it more interesting and unique. This is definitely one of the most complex projects I’ve worked on.

The project folder contains:
app.py  (main program that handles the backend)
helper.py (all the helper functions used in app.py)
Template folder that contains all the HTML for different pages
Style.css which handles the appearance
account.db which uses SQLite to store all the data


The app.py contains the most functions. To start off, it handles the login and register process, the function checks the user input to see if it meets the requirement of username and password. If both are valid the program searches through the account.db to see if the username is already taken, if not, the newly registered account is stored using SQLite, with the new username registered into the database while the password is hashed and encrypted and stored in the database.

This part was pretty challenging as there are many requirements for username and password, and the error messages are all tailored to a specific error so it can guide the user in the right direction. Storing users using SQLite means I also had to create tables with appropriate columns and datatypes that can store all the important user information

After logging in using a valid username and password, the user is directed to the home page where it shows the user’s current balance and assets. This is also done by accessing the SQLite database of that specific user using their ID. All users start with $0 and no assets under their account. The table on the home page shows the crypto symbol, average price, total price and the amount of tokens owned.

All the HTML templates are built using the skeleton template called layout.html. The data is processed using Python through app.py and Flask and Jinja transfers the data to display using HTML. Linking all three together is a very tedious process but it allows the data to be manipulated and processed. Python accesses the SQLite database using the db.execute() command. It is a helper function provided by CS50 to make the connection between SQLite and Python easier. When designing the program, I considered using the proper SQLiteite library to set up the connection. However, I realised it would complicate the program and would make it even more challenging. As a result, I’ve decided to stick with the CS50 version so I have one less thing to worry about while working on this complex project.

The helper.py contains many useful helper functions that are utilised in app.py. Similar to the problem set in week 9. There is a lookup function that collects all the essential information of a crypto, such as its price and symbol. The lookup function uses the Binance API which with proper manipulation can output a dictionary that contains the crypto symbol and price. If the crypto symbol is invalid and cannot be found through Binance, the function will return false which tells the user that the symbol they’ve entered is invalid. Another helper function is aud(), since Binance collects information in USD, the aud function, converts the currency and displays the balance in a cleaner manner ($ symbol and fixed floating point).

The watchlist page allows the user to add their favourite crypto to the watchlist. When added the time, crypto symbol, and current price are provided, alongside a ‘remove’ and ‘update’ button. The display of the table uses a similar process as the table on the home page, when a user adds a crypto to the watchlist using the provided input field, the lookup function is used to collect the information and the DateTime library records the time when it occurred. All this information is then stored using SQLite and accessed using Flask, Python and Jinja to display to the user. The remove button sends a value equal to the crypto symbol so in app.py the program knows which cryptocurrency to remove from the watchlist database. The update button has a similar function but simply calls the lookup function again to update the price, and uses dateTime to update and display the corresponding time.

The trade page consists of four buttons, buy, sell, withdraw and deposit. This page is where all the transaction occurs. Using JavaScript, the layout of the page changes depending on the button pressed. All four types of transactions have their unique error detection and inform the users when it has occurred. For example, the withdrawal amount cannot be greater than the current balance, the buy amount cannot be greater than the current balance the crypto symbol has to be valid. When selling crypto, a dropdown selection is used so the users can only select the cryptos they own. All the arithmetic calculation is done in the Python app.py. If the transaction is successful all the information is stored using SQLite which contains the user ID, crypto symbol, token amount, price, total and transaction type. All this information is stored in the asset table in SQLiteite, which is also used for the history page.

The history page displays all the transactions that have occurred under the current user ID, it simply accesses the asset table in SQLite and displays the information in a table
