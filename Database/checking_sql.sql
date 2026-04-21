Select * from users;
TRUNCATE TABLE 
    project_members, 
    tasks, 
    users, 
    projects, 
RESTART IDENTITY CASCADE;