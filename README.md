Introduction



This is my 4th year graph theory project. For this project I was required to design a database for a timetabling system for our university. The database stores data about student groups, classrooms, lecturers, work hours and other data relating to timetables. This is the design document for the project.

Understanding the problem


The timetabling problem, in its simplest form, is trying to allocate shared resources to a given timeslot. These resources include lecturers, rooms and student groups. These resources are limited and must be scheduled in such a way that they are uniquely allocated per timeslot.

Understanding Neo4J


Before trying to solve the timetabling problem it is important to first understand Neo4J and how it works.

What is Neo4J?


Neo4J is a graph database management system. Unlike relational databases, NoSQL(Not only SQL) databases do not follow a set schema. This allows the data to be more flexible. Graph databases are particularly useful for storing connections, or relationships, between data.

How does Neo4J store data?
All data in a Neo4J database is represented as one of the following five structures:

Nodes

A node in Neo4J is similar to a record in a relational database.

Labels

Nodes can have labels. Labels are used to associate a set of nodes. Nodes with the same label are grouped together. In a relational database labels would be equivalent to tables.

Relationships

Relationships are what connect the nodes in the graph. Neo4J is a multi-directional graph meaning the relationships, or edges, have direction. However, this direction can be ignored in queries. There can also be more than one relationship between any two nodes. Relationships can be compared to joins in relational databases, but because they are predefined it is much faster.

Relationship types

Relationship types are used to describe how two nodes are related to each other. This is usually a verb. Relationship types are mandatory in Neo4J.

Properties

Properties are key-value pairs that store data in nodes and relationships. As mentioned before, Neo4J is schemaless, therefore each node or relationship can have different properties even if they have the same labels or relationship types. Properties are similar to columns in relational databases.

What data needs to be stored?
Analysing both the problem, and the current DTU timetabling system, helped determine what data this system needs to store. A brief break down is given below.

College

The college using this timetabling system.

Campus

The college may have different campuses.

Rooms

Rooms will be identified by room numbers. Every room has a capacity and a type, such as lecture room, computer room and so on. Each room is within a campus.

Department

Each campus is divided into one or more departments.

Course

Each department can run several courses. Courses are identified by an id and name.

Modules

Each course has several modules. Modules are also identified by an id and name. More than one lecturer can teach a single module. Also, many courses can share the same module. Modules also change depending on the semester.

Year groups

Year groups are identified by a unique code and are divided into student groups.

Student groups

Student groups are identified by a combination of the year group and a group name, for example, group A, B and C. Each student group will have a different size that must be accounted for. However, it is not necessary to store all students as separate nodes.

Lecturers

Lecturers are identified by their staff Id and name. Their maximum working hours should be stored. Each lecturer works for a department in a campus.

Classes

Classes are identified by a combination of the time and day for which it is scheduled. Classes will also have a duration, type which will correspond with the type of classroom is required, a lecturer and will also belong to a module.

Researching solutions
Before trying to solve this problem I researched solutions and techniques proposed by others to solve this problem. Graph Colouring seemed to be a very common approach when dealing with the timetabling problem. It can be divided into vertex and edge colouring.

Vertex colouring It is a way of colouring the vertices of a graph such that no two adjacent vertices share the same colour.

Edge colouring It is a way of colouring the edges of a graph such that no two adjacent edges share the same colour.

"Colouring" a vertex or edge simply means giving it a label. Many algorithms exist to colour a graph with the minimum amount of colours. This is called the chromatic number. In relation to the timetabling problem, vertex colouring can be used to create a graph like the following.

An example of a coloured graph

In this graph the vertices could represent classes. The edges could represent conflicts between classes. For example, if two classes share the same room, student group or lecturer. The colours could represent the timeslot in which that particular class is scheduled for. When constructing the timetable graph we know that in order to avoid a conflict we must not connect two nodes of the same colour. The maximum amount of colours the graph can have in this case is equal to the number of timeslots available in a week.

Adding the data to the database
Once the data is obtained we can start storing it in the prototype database. This section will involve importing the CSV files created earlier into the Neo4J database.

The first node that needs to be created is the college node. The following query will create a single college node with a single property called name with the value 'DTU'.

CREATE (c:College {name: "DTU"});
Next create the room and campus nodes from the rooms.csv file, as shown below. This query first loads the rooms.csv file from the import folder.

LOAD CSV WITH HEADERS FROM "file:///rooms.csv" AS line
MERGE (r:Room { name: line.name, capacity: toInteger(line.capacity) })
MERGE (c:Campus { name: line.campus })
MERGE (c)-[:HAS]->(r);
Then, to create relationships between the college and campus nodes, use the MATCH keyword to find the college node that was created in the first query and all the campus nodes. Using CREATE we can then create a relationship between the college node and all the campus nodes.

MATCH (col:College {name: "DTU"}), (c:Campus)
CREATE (col)-[:HAS]->(c);
Next, we'll create the department nodes and the relationships between the new departments and the campus nodes to which they belong. This data will be loaded from the departments.csv file. Again, using the MERGE keyword, create the department and campus nodes if they do not already exist. Then create a relationship between them.

LOAD CSV WITH HEADERS FROM "file:///departments.csv" AS line
MERGE (d:Department { name: line.name })
MERGE (c:Campus { name: line.campus })
MERGE (c)-[:HAS]->(d);
Using a similar query to the one above we can create all course and year group nodes. This is a slightly longer query as the courses.csv contains a lot of different data. First, USING the match keyword, find the department node with a name value that matches the department column in the line of data. Next, using MERGE, check if a course node with the given course code exists. If not, create it. Then set the properties title and level.

LOAD CSV WITH HEADERS FROM "file:///courses.csv" AS line
MATCH (d:Department { name: line.department })
MERGE (c:Course { course_code: line.course_code })
SET c.title = line.title
SET c.level = toInteger(line.level)
MERGE (d)-[:RUNS]->(c)
MERGE (c)-[:ENROLLS]->(y:Year_Group { year_code: line.year_code })
SET y.year = toInteger(line.year);
Next create the lecturers for the Mathematics and Computing department, using the data from the lecturers.csv file, as shown below.

LOAD CSV WITH HEADERS FROM "file:///lecturers.csv" AS line
CREATE (l:Lecturer { id: line.id, name: line.name, work_hours: toInteger(line.work_hours) })
MERGE (d:Department { name: line.department })
MERGE (d)-[:EMPLOYS]->(l);
Create modules for the Mathematics and Computing, using the data from the modules.csv file. This file contains an array of lecturer names which will have to be handled. To do this, first use substring to remove the square brackets. Next, split the array using a comma as a delimiter. Then, use the UNWIND keyword to separate the array into multiple rows of data. Next, use MATCH to find the course using the course_code property and from that find the 3rd year node. Create the new module node and a relation between the year group and it. Finally, create a TEACHES relationship between the lecturer and module. Note that it is not a good idea to find the lecturer by name as more than one lecturer might have that name, however, staff Id's were not available when obtaining the data.

LOAD CSV WITH HEADERS FROM "file:///modules.csv" AS line
WITH line, split(substring(line.lecturers, 1, size(line.lecturers) -7), ",") AS lecturers 
UNWIND lecturers AS lecturer_name
MATCH (c:Course { course_code: "KSOFG", level: 7 })-[r]->(y:Year_Group { year: 3 })
MERGE (m:Module { module_code: line.module_code, name: line.name, semester: toInteger(line.semester) })
MERGE (y)-[:STUDIES]->(m)
MERGE (l:Lecturer { name: lecturer_name })
MERGE (l)-[:TEACHES]->(m);
Finally, create the class nodes from the data in the classes.csv file. Create relationships between the new class node and the lecturer, module and room nodes.

LOAD CSV WITH HEADERS FROM "file:///classes.csv" AS line
MATCH (r:Room { name: line.room })
MATCH (m:Module { name: line.module_name })
CREATE (cl:Class { day: toInteger(line.day), start: toInteger(line.start), end: toInteger(line.end), group: line.group_name, type: line.type })
MERGE (m)-[:SUBJECT_OF]->(cl)
MERGE (r)-[:HOSTS]->(cl);
:config initialNodeDisplay:1000
MATCH (n)-[r]->(m) RETURN n, r, m;
Another important feature of a timetabling system was being able to display available rooms. The following query will find all room nodes with a capacity of at least 20 that are connected to a campus node with the name "Incline Wing". If the room is connected to one or more class nodes ensure the room is only returned if it is not occupied at the given day and time

MATCH (campus:Campus { name: "DEPARTMENT1" })-[r]->(room:Room)
WHERE room.capacity >= 20
OPTIONAL MATCH (room)-[r1:HOSTS]->(class:Class)<-[r2:SUBJECT_OF]-(module:Module { semester: 7 })
WITH room, COLLECT(class) AS classes
WHERE ALL(class IN classes
WHERE class.day <> 3 OR
(10 < class.start AND 11 <= class.start) 
OR (11 > class.end AND 10 >= class.end))
RETURN DISTINCT room
ORDER BY room.capacity;
To get the lecturers weekly working hours we can use a similar query and change the return statement

MATCH (lecturer:Lecturer { name: "Payal Ma'am" })-[teaches:TEACHES]->(module:Module { semester: 7 })
MATCH (module)-[subject_of:SUBJECT_OF]->(class:Class)
MATCH (room:Room)-[hosts:HOSTS]->(class)
RETURN SUM(class.end - class.start) AS working_hours;

References:

Neo4J
Graph colouring on Wikipedia
Cypher cheat sheet
Importing CSV files with Cypher
Importing CSV files containing array
