## ASKFORTRANSPORT
***
>Our project is our attempt to create a larger market for transporters of bulk goods by providing a platform where they can advertise their services to prospective customers.

### Motivation
***
>Transportation of goods in bulk is a common need in our day to day business activities.

>The process of finding transport tends to be quite cumbersome for most people. This is because in as much as someone has in mind exactly the kind of transportation they require, depending on their needs, they might not know where to get this service from. They are not exposed to enough options, and the ones which are accessible might not meet their kind of need.
We also have a lot of vehicle owners offering transportation services. Although these people might be popular locally, they may miss out on more opportunities as they don’t have a way to improve their customer reach. They are mostly dependent on walk-ins and referrals.

>Our platform connects people looking for transport with those offering a transportation services. This is our target audience.

### Setting up the development environment
***
1) Clone the repository git clone https://github.com/JerryNyoike/askfortransport.git
2) Install 
    - [Python](https://www.python.org/downloads/)
    - [MySQL](https://dev.mysql.com/doc/refman/8.0/en/installing.html)

3) Set up a [virtual environment](https://docs.python.org/3/tutorial/venv.html) in the root folder of the project using the command `python3 -m venv .` while inside the project folder
4) Install project dependencies using [pip](https://pip.pypa.io/en/stable/installing/) by executing the command `pip3 install -r requirements.txt` when inside the root directory.
> List of project dependencies
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/)
- [PyJWT](https://pyjwt.readthedocs.io/en/latest/)
- [PyMySQL](https://pymysql.readthedocs.io/en/latest/)
5) Create a database instance using the command `mysql source app/schema.sql` from the project's root directory.
6) Run the Flask server with the commands 
    ```
    $export FLASK_ENV=development
    $export FLASK_APP=lig.py
    $flask run
    ```

### Contributors
***
1) [Braxton Muimi](https://github.com/Brackie)
2) [Jerry Nyoike](https://github.com/JerryNyoike)