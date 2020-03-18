# RMSA
Report Management System Assessment

## Assessment Instructions
Let’s say that you have a large set of reports and each report has many files related to it like pictures/sound files and each report is classified under different tags, like “Technology”, “Sports”, “Medical” etc. And each of these reports is belonging to different types of groups like “Saudi Arabia”, “US”, “General” etc.
Now the purpose is to organize these reports for searching and fast retrieval.
Requirements:
1. Users Management (CRUD).
  - Each user must have a login, and a role assigned to him/her for viewing, editing and
deleting documents.
  - Assign users to different groups. Each user will be given the ability to
view/edit/delete/create a report on different groups by the admin. (e.g. when a report is belonging to Group A and user doesn’t have permission for Group A then he/she shouldn’t be able to even see reports under this group).
  - A user can have the permission for 1 or more groups.
2. Roles Management (CRUD).
  - Admin, User. And Admin has full authority and can delete other users and assign users to different groups.
3. Group Management (CRUD).
4. Search using different criteria.
  - By report name.
  - By content.
  - By tag.
  - By group.
  - By editor/uploader.
5. Report CRUD.
  - Create a new report that includes the tags, group, and related files.

Candidates should keep three things in mind while implementing this project:
1. Consider that a large set of reports already are existing and need to ported to this system.
2. Consider that a new report will be uploaded to the system.
3. Consider the authority for viewing reports according to the user allowed groups and role.


## Running the Application
The assessment above was implement as a web application. The project was developed
in Python-flask for the web application and Mysql relational database for data
storage. To run the application locally, follow the steps below.

Note: you can point the application to your own database using your credentials by changing the
the database information in `__init__.py` for the application and `create_and_seed_db.py` for seeding.

1. Ensure you have the following installed on your system:
  - `git 2.20`
  - `Mysql 8.0` Ensure you have a user `root` with no password in Mysql to allow the application access
  - `Python 3.7`
  - Python 3 `Pip 20.0`
2. Download the code from the Github repository
  - Clone the repository containing the code by executing:
    ```
    $ git clone https://github.com/sfm2686/RMSA.git
    ```
  - Navigate inside the cloned directory of the project
    ```
    $ cd RMSA
    ```
3. Install project dependencies in a Python virtual environment(if you wish  to install the dependencies systemwide you can skip to the last command in this step although its not recommended):
  - Using `pip`, install `virtualenv`, (assuming `pip` here is pointing
    to your Python 3's pip executable, otherwise you probably can use `pip3` instead):
    ```
    $ pip install virtualenv
    ```
  - Create a new virtual environment using `virtualenv` called `venv`,
    (assuming `python` here is pointing to your Python 3 executable,
      otherwise you probably can use `python3` instead):
    ```
    $ python -m virtualenv venv
    ```
  - Activate the virtual environment:
    ```
    $ . venv/bin/activate
    ```
  - Install project dependencies in the virtual environment:
    ```
    (venv)$ pip install -r requirements.txt
    ```
4. Create and seed the database:
  - The `create_and_seed_db.py` script recreates the database and seeds it with dummy
    data. The script generates data for every table in the database, including users, roles,
    dummy groups, dummy files and dummy reports along with randomized relationships between entities
  - The default auto-generated admin user in the system has the username of `sultanmira` and password `adminadmin`.
    Other auto-generated users by the script have their password the same as their usernames
  - The script takes two command-line arguments, `nreports` and `nfiles` representing
    the number of reports and files to be generated respectively. If no arguments are passed,
    the default values are `1000` reports and `600` files
  - To run the script:
    ```
    (venv)$ python create_and_seed_db.py 1000 600
    ```
5. Run the application:
  ```
  (venv)$ python app.py
  ```
6. Open the application in a web browser using the url: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Assumptions and Impacts:
This section mentions the assumptions the developer had at the time of development when facing
unclear requirements and the impacts those assumptions had on the system.

#### Assumption #1
Admins can see all groups in the system even the ones they dont belong to.
##### Impact
Admins are able to perform CRUD operations on all groups in the system.

#### Assumption #2
Typically, files related to reports will be unique (each file will belong to one report only)
##### Impact
This assumption directly impacted the relationship in the database between the `reports` and `files` tables.
Because of this assumption the relationship was modeled to be M-1 instead of M-M, which would have required
a junction table linking reports and files to be achieved.

#### Assumption #3
Typically, reports will be unique across the entire system (different groups will not have the same reports)
and each report belongs to one group only.
##### Impact
This assumption had the same impact as Assumption #2 but on the relationship between the `reports` table and the `groups_table`.

#### Assumption #4
Tags, roles and file types(media types) are predefined in the system and dont support CRUD operations.
##### Impact
The database has to be seeded with initial reference information and for media types, the enum class
has to be hard-coded.

## Future Improvements
This section mentions the improvements and enhancements I would implement in the application in the future.
1. Utilize docker and docker-compose for each the flask application and the database to make deployment easier
2. Enhance the UI and UX of the application by including a front-end framework such as Reactjs or Vuejs and implement more specific error messages and front-end validation
3. Factor out the repeated logic and operations to helper functions or other modules
4. Break `views.py` into a number of smaller files for better maintainability and readability
5. Utilize `Flask-wtf` forms instead of raw html
