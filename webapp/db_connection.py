import mysql.connector #imports the library that is needed to conect to a mysql database
from mysql.connector import errorcode #imports the method errorcode to see what error has ocurred if any error happens

def databaseconnection(): #function to connect to the database
    try:
        cnx = mysql.connector.connect(user='root',password='', database='la_trobada') #this line is used to stablish connection with the database, user is the user of the db, password is the password for the user and database is the database that we want the app to connect
        return cnx #it returns the conexion stablished 
    except mysql.connector.Error as err: #it catches the error if any problem happens
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR: #compares if the error is Acces denied
            print("Incorrect user") 
            cnx.close() #closes the conncetion
        elif err.errno == errorcode.ER_BAD_DB_ERROR: #compares if the error is database doesn't exist
            print("database doesn't exist")
            cnx.close() #closes the conncetion
        else:
            print(err)  #if there is other error rather than the 2 above it will directly print the error
            cnx.close() #closes the conncetion