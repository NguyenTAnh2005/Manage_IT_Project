Select * from users;
Select * from project_members;
Select * from tasks;
Select * from projects;

TRUNCATE TABLE 
    project_members, 
    tasks, 
    users, 
    projects
RESTART IDENTITY CASCADE;