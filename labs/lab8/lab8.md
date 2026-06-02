# Apache Cassandra Tutorial
## Learning Objectives
- Explain what Apache Cassandra is and when it is useful.
- Compare Cassandra with relational databases and other NoSQL databases.
- Install and run Cassandra locally using Docker.
- Use `cqlsh` to create keyspaces, create tables, insert data, query data, update data, delete data, and export data.
- Complete a small hands-on lab using Cassandra Query Language, or CQL.

## 1. Apache Cassandra
Apache Cassandra is an open-source, distributed NoSQL database. It is often used when an application needs to handle a large amount of data across many machines while remaining available even if some machines fail.

Cassandra is a wide-column database. It stores data in tables, but tables are usually designed around the queries the application needs to run.

Cassandra uses **CQL**, or Cassandra Query Language. CQL looks similar to SQL because it uses familiar ideas such as tables, rows, columns, `SELECT`, `INSERT`, and `CREATE TABLE`.

## Cassandra vs. Relational Databases and Other NoSQL Databases
### Cassandra vs. Relational Databases
| Feature        | Relational DB, e.g. PostgreSQL/MySQL                | Cassandra                                                           |
| -------------- | --------------------------------------------------- | ------------------------------------------------------------------- |
| Data model     | Tables with normalized relationships                | Wide-column tables designed for queries                             |
| Query language | SQL                                                 | CQL                                                                 |
| Joins          | Common                                              | Not supported in the same way                                       |
| Transactions   | Strong ACID transactions are common                 | Limited transaction support; optimized for distributed availability |
| Schema design  | Entity-first, normalize data                        | Query-first, denormalize data                                       |
| Scaling        | Often vertical first, then sharding/replication     | Horizontal scaling is central                                       |
| Best for       | Complex queries, joins, reports, strict consistency | Large-scale writes, high availability, predictable access patterns  |

In a relational database, you usually design normalized tables first, then write queries using joins. In Cassandra, you usually start from the queries and design tables to answer those queries efficiently.

### Cassandra vs. MongoDB
| Feature          | MongoDB                                            | Cassandra                                            |
| ---------------- | -------------------------------------------------- | ---------------------------------------------------- |
| Type             | Document database                                  | Wide-column database                                 |
| Data unit        | JSON-like document                                 | Row in a partitioned table                           |
| Flexible schema  | Very flexible                                      | Flexible columns, but table/query design is stricter |
| Query model      | Rich document queries                              | Query by partition key and clustering columns        |
| Common use cases | Content management, product catalogs, app backends | Time-series data, event logs, large-scale writes     |

MongoDB is often easier when the data is naturally document-shaped and queries need flexibility. Cassandra is stronger when the workload is massive, distributed, write-heavy, and query patterns are known in advance.

Cassandra is a good fit for:

- High-volume write-heavy workloads.
- Event logging.
- Time-series data.
- User activity tracking.
- Recommendation-event storage.

Cassandra is usually not the best first choice for:

- Small applications with simple relational needs.
- Applications requiring many joins.
- Strong transactional consistency across many rows and tables.

## 2. Core concepts
### 2.1. Cluster, Node, and Data Center
A Cassandra deployment is usually made of multiple machines.

| Term        | Meaning                                                                                                    |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| Node        | A single Cassandra server.                                                                                 |
| Cluster     | A group of Cassandra nodes working together.                                                               |
| Data center | A logical grouping of nodes, often corresponding to a physical region, cloud region, or availability zone. |
| Keyspace    | Similar to a database namespace. It defines replication settings for tables.                               |
| Table       | A collection of rows. Tables are designed around query patterns.                                           |

For this tutorial, we will use a single-node local Cassandra instance through Docker. This is enough for learning CQL and basic data modeling.

### 2.2. Keyspace
A **keyspace** is the top-level namespace in Cassandra. It stores tables and defines replication options. In CQL, `CREATE KEYSPACE` requires a replication configuration.

Example
```SQL
CREATE KEYSPACE demo
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};
```

### 2.3. Table, Primary Key, Partition Key, and Clustering Columns
Cassandra tables require a primary key. The primary key controls both uniqueness and data distribution.

The partition key determines where data is stored in the cluster. Rows with the same partition key are stored together.

## 3. Installation Guide
This tutorial uses Docker because it is the simplest and most reproducible setup for students. Let's first open the EC2 instance and check the docker status:
```
docker --version
``` 

Then set the docker permission by using the command
```
sudo chmod 666 /var/run/docker.sock 
```

Pull the Cassandra Docker Image:
```
docker pull cassandra:latest
```

Start Cassandra
```
docker run --name cassandra-demo -p 9042:9042 -d cassandra:latest
```

| Part                    | Meaning                         |
| ----------------------- | ------------------------------- |
| `docker run`            | Start a new container           |
| `--name cassandra-demo` | Give the container a name       |
| `-p 9042:9042`          | Expose Cassandra’s CQL port     |
| `-d`                    | Run in detached/background mode |
| `cassandra:latest`      | Use the Cassandra Docker image  |

Wait about 30–60 seconds for Cassandra to initialize.

Check logs:
```
docker logs cassandra-demo
```

### Connect with `cqlsh`
cqlsh is Cassandra’s command-line shell for interacting with Cassandra using CQL. Run (make sure Cassandra has been initialized):
```
docker exec -it cassandra-demo cqlsh
```

You will see prompt similar to
```
cqlsh>
```

Exit cqlsh first if needed:
```
exit;
```

Stop Cassandra:
```
docker stop cassandra-demo
```

Start it again:
```
docker start cassandra-demo
```

Remove it completely:
```
docker rm -f cassandra-demo
```

## 4. Basic CQL Commands
Enter cqlsh:
```
docker exec -it cassandra-demo cqlsh
```

Show Existing Keyspaces
```
DESCRIBE KEYSPACES;
```

Create a Keyspace
```
CREATE KEYSPACE music_app
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};
```

Use a Keyspace
```
USE music_app;
```

Create a table
```
CREATE TABLE songs_by_artist (
  artist text,
  release_year int,
  song_id uuid,
  title text,
  album text,
  genre text,
  PRIMARY KEY (artist, release_year, song_id)
);
```

Describe Tables
```
DESCRIBE TABLES;
```
```
DESCRIBE TABLE songs_by_artist;
```

Insert Data

Insert into `plays_by_user`
```
INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u1', '2026-05-01 10:00:00', 's1', 'Taylor Swift', 'Anti-Hero', 'iphone');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u1', '2026-05-01 10:05:00', 's2', 'The Weeknd', 'Blinding Lights', 'iphone');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u1', '2026-05-01 10:10:00', 's3', 'Billie Eilish', 'bad guy', 'laptop');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u2', '2026-05-01 11:00:00', 's1', 'Taylor Swift', 'Anti-Hero', 'android');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u2', '2026-05-01 11:15:00', 's4', 'Olivia Rodrigo', 'drivers license', 'tablet');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u3', '2026-05-01 12:00:00', 's1', 'Taylor Swift', 'Anti-Hero', 'laptop');
```

Insert into `plays_by_song`
```
INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s1', '2026-05-01 10:00:00', 'u1', 'Taylor Swift', 'Anti-Hero', 'iphone');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s2', '2026-05-01 10:05:00', 'u1', 'The Weeknd', 'Blinding Lights', 'iphone');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s3', '2026-05-01 10:10:00', 'u1', 'Billie Eilish', 'bad guy', 'laptop');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s1', '2026-05-01 11:00:00', 'u2', 'Taylor Swift', 'Anti-Hero', 'android');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s4', '2026-05-01 11:15:00', 'u2', 'Olivia Rodrigo', 'drivers license', 'tablet');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s1', '2026-05-01 12:00:00', 'u3', 'Taylor Swift', 'Anti-Hero', 'laptop');
```

Query Data
```
SELECT *
FROM plays_by_user
WHERE user_id = 'u1';
```

Update Data
```
UPDATE plays_by_user
SET device = 'iphone'
WHERE user_id = 'u2'
  AND played_at = '2026-05-01 11:00:00'
  AND song_id = 's1';
```

Delete Data
```
DELETE FROM plays_by_user
WHERE user_id = 'u2'
  AND played_at = '2026-05-01 11:15:00'
  AND song_id = 's4';
```

Drop a Table
```
DROP TABLE plays_by_user;
```

Drop a Keyspace
```
DROP KEYSPACE music_app;
```

## 5. Exporting and Importing Data
Cassandra’s `cqlsh` supports `COPY TO` for exporting table data to CSV and COPY FROM for loading CSV data into a table.

Because we are running Cassandra inside Docker, paths used by `COPY` refer to **paths inside the container**.

Export a Table to CSV:
```
COPY music_app.songs_by_artist
TO '/tmp/songs_by_artist.csv'
WITH HEADER = TRUE;
```
Exit `cqlsh`:
```
exit;
```

Copy the exported file from the container to your local machine/ ec2 instances:
```
docker cp cassandra-demo:/tmp/songs_by_artist.csv ./songs_by_artist.csv
```

## Lab Assignment: Music Listening Events in Cassandra
In this lab, you will design a small Cassandra database for music listening events. You will create two query-oriented tables, load sample data, run queries, update data, delete data, and export results to CSV.

### Scenario

A music streaming app wants to store listening events. Each event contains:

- user_id
- song_id
- artist
- title
- played_at
- device

The app needs to answer two queries:

1. For a given user, what songs did they recently play?
2. For a given song, which users recently played it?

#### Part A: Start Cassandra
Start Cassandra using Docker

#### Part B: Create a Keyspace
Create a keyspace called `music_lab`. Then use the keyspace.

#### Part C: Create Two Tables
Create a table for query 1:
```
CREATE TABLE plays_by_user (
  user_id text,
  played_at timestamp,
  song_id text,
  artist text,
  title text,
  device text,
  PRIMARY KEY (user_id, played_at, song_id)
) WITH CLUSTERING ORDER BY (played_at DESC);
```

Create a table for query 2:
```
CREATE TABLE plays_by_song (
  song_id text,
  played_at timestamp,
  user_id text,
  artist text,
  title text,
  device text,
  PRIMARY KEY (song_id, played_at, user_id)
) WITH CLUSTERING ORDER BY (played_at DESC);
```

#### Part D: Insert Sample Data
Insert into `plays_by_user`
```
INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u1', '2026-05-01 10:00:00', 's1', 'Taylor Swift', 'Anti-Hero', 'iphone');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u1', '2026-05-01 10:05:00', 's2', 'The Weeknd', 'Blinding Lights', 'iphone');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u1', '2026-05-01 10:10:00', 's3', 'Billie Eilish', 'bad guy', 'laptop');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u2', '2026-05-01 11:00:00', 's1', 'Taylor Swift', 'Anti-Hero', 'android');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u2', '2026-05-01 11:15:00', 's4', 'Olivia Rodrigo', 'drivers license', 'tablet');

INSERT INTO plays_by_user
(user_id, played_at, song_id, artist, title, device)
VALUES
('u3', '2026-05-01 12:00:00', 's1', 'Taylor Swift', 'Anti-Hero', 'laptop');
```

Insert into `plays_by_song`
```
INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s1', '2026-05-01 10:00:00', 'u1', 'Taylor Swift', 'Anti-Hero', 'iphone');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s2', '2026-05-01 10:05:00', 'u1', 'The Weeknd', 'Blinding Lights', 'iphone');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s3', '2026-05-01 10:10:00', 'u1', 'Billie Eilish', 'bad guy', 'laptop');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s1', '2026-05-01 11:00:00', 'u2', 'Taylor Swift', 'Anti-Hero', 'android');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s4', '2026-05-01 11:15:00', 'u2', 'Olivia Rodrigo', 'drivers license', 'tablet');

INSERT INTO plays_by_song
(song_id, played_at, user_id, artist, title, device)
VALUES
('s1', '2026-05-01 12:00:00', 'u3', 'Taylor Swift', 'Anti-Hero', 'laptop');
```

#### Part E: Run Queries
- Query 1: return all plays by user `u1`, ordered by `played_at` descending.

- Query 2: all users who played song `s1`, ordered by `played_at` descending.

- Query 3: all the plays of user `u1` happened after `2026-05-01 10:05:00' 

#### Part F: Export Data
Export `plays_by_user` and `plays_by_song`

### Part G: Questions for Submission

Submit a short Markdown file answering the following questions:

1. What is the partition key of plays_by_user?
2. What are the clustering columns of plays_by_user?
3. Why did we create both plays_by_user and plays_by_song instead of using one table?
4. What happens if you try to query plays_by_user by song_id only?
5. Why is data duplication common in Cassandra?
6. Include a screenshot or copied output of:
        - SELECT * FROM plays_by_user WHERE user_id = 'u1';
        - SELECT * FROM plays_by_song WHERE song_id = 's1';
7. Submit the two exported CSV files:
        - plays_by_user.csv
        - plays_by_song.csv

### Cleanup
After finishing the lab, stop and remove the container:
```
docker rm -f cassandra-lab
```

## Appendix: Common Cassandra / CQL Commands Cheat Sheet
### Docker Commands
```
docker pull cassandra:latest
docker run --name cassandra-demo -p 9042:9042 -d cassandra:latest
docker logs cassandra-demo
docker exec -it cassandra-demo cqlsh
docker exec -it cassandra-demo nodetool status
docker stop cassandra-demo
docker start cassandra-demo
docker rm -f cassandra-demo
```

### Keyspace Commands
```
DESCRIBE KEYSPACES;

CREATE KEYSPACE keyspace_name
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};

USE keyspace_name;

DROP KEYSPACE keyspace_name;
```

### Table Commands
```
DESCRIBE TABLES;

DESCRIBE TABLE table_name;

CREATE TABLE table_name (
  id text PRIMARY KEY,
  value text
);

DROP TABLE table_name;

TRUNCATE table_name;
```

### Data Commands
```
INSERT INTO table_name (id, value)
VALUES ('1', 'hello');

SELECT * FROM table_name
WHERE id = '1';

UPDATE table_name
SET value = 'updated'
WHERE id = '1';

DELETE FROM table_name
WHERE id = '1';
```

### Export / Import Commands
```
COPY table_name TO '/tmp/output.csv' WITH HEADER = TRUE;

COPY table_name FROM '/tmp/input.csv' WITH HEADER = TRUE;
```
