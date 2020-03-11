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


Assumptions:
- Admins can see all groups in the system even the ones they dont belong to
- Typically, files related to reports will be unique (different reports will not typically have the same files)
- Typically, reports will be unique across the entire system (different groups will not have the same reports)
and each report belongs to one group only
- Tags, roles and file types(media types) are predefined in the system and dont support CRUD operations
