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


## Installation Instructions
This project was developed in Python-flask for the web application and Mysql
relational database for data storage. To install and run the application locally,
follow the steps below.

1. Ensure you have the following installed on your system:
  - `Mysql 8.0`
  - `Python 3.7`
  - Python 3 `Pip 20.0`
2. Install project dependencies in a Python virtual environment:
  - Using `pip`, install `virtualenv`, (assuming `python` here is pointing
    to your Python 3 executable, otherwise you probably can use `python3` instead):
    ```
    $ pip install virtualenv
    ```
  - Create a new virtual environment using `virtualenv`,
    (assuming `python` here is pointing to your Python 3 executable,
      otherwise you probably can use `python3` instead):
    ```
    $ python -m virtualenv venv
    ```
  - Activate the newly made virtual environment:
    ```
    $ . venv/bin/activates
    ```
  - Install project dependencies in the virtual environment:
    ```
    $ pip install -r requirements.txt
    ```
3. Create and seed the database:
  - The `create_and_seed_db.py` script recreates the database and seeds it with dummy
    data. The script generates data for every table in the database, including users, roles,
    dummy groups, dummy files and dummy reports. The default admin in the system has the username
     of `sultanmira` and password `adminadmin`. Other users in the system have their password the same as their usernames.
  - The script takes two command-line arguments, `nreports` and `nfiles` representing
    the number of reports and files to be generated respectively. If no arguments are passed,
    the default values are `1000` reports and `600` files.
  - To run the script:
    ```
    $ python create_and_seed_db.py 1000 600
    ```
4. Run the application:
  ```
  $ python app.py
  ```

Assumptions:
- Admins can see all groups in the system even the ones they dont belong to
- Typically, files related to reports will be unique (different reports will not typically have the same files)
- Typically, reports will be unique across the entire system (different groups will not have the same reports)
and each report belongs to one group only
- Tags, roles and file types(media types) are predefined in the system and dont support CRUD operations
