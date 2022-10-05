## Requirements ##
* MySQL
* Python and pip module.

If you have these, then install the necessary packages and libraries stated in the requirements.txt one by one or run the following code:
```pip install -r requirements.txt```
In order to prevent any possible conflicts, you can set up a virtual environment. You can learn more about virtual environments on [here](https://docs.python.org/3/library/venv.html#module-venv) and it is highly recommended.

## Deployment ##
After installation, create a database from the MySQL Shell using the following command series:
```\sql```
```\connect root@localhost```
```create database simpleboundb;```
```use simpleboundb;``` 

Then, to create triggers and procedures, use the sql queries which is placed under the ```sql``` folder. There are 5 triggers and a procedure. Use MySQL Shell or MySQL Workbench to run the queries. Workbench 8.0 CE is recommended.

Apart from that, creating additional database will come in handy, and the reason behind that is to have a clean database. Please, run the following command too from MySQL Shell:
```create database config;```

Make sure that you change the ```MYSQL_PASSWORD``` from the ```.env``` file to your root user's password. Of course, you may use other users or hosts or database names to run the program, but that may require additional changes to the ```.env``` and ```setting``` files. It is recommended that you use these configurations. Using these configurations should make your database clean in terms of additional relations which comes with migrations.

After that, ensure that your database server is up and run these commands to set up the database to Django configurations:
```cd simpleboun```
```python manage.py migrate```

Note that there is already a migrations folder under ```./registration```. You may need to delete it before migration.

After the creation of database, triggers and procedures, run createdb.py to create tables and for some initial values using the following command:
```python ./simpleboun/createdb.py```

Finally, run the command:
```python manage.py runserver```
and check whether the website is accessible at: [http://127.0.0.1:8000/registration/](http://127.0.0.1:8000/registration/)





