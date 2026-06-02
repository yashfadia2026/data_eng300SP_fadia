1. What is the partition key of plays_by_user?
The partition key of plays_by_user is user_id.

2. What are the clustering columns of plays_by_user?
The clustering columns of plays_by_user are 'played_at' and 'song_id'.

3. Why did we create both plays_by_user and plays_by_song instead of using one table?
Tables in Cassandra are designed around specific query patterns. plays_by_user was designed to help find all the recent songs that are played by any given user, while the plays_by_Song was designed to identify all the users who have recently played a given song. Thus, both these tables were needed to answer the required questions.

4. What happens if you try to query plays_by_user by song_id only?
This query will be rejected by Cassandra because song_id is not the partition key for that table. Usually, the partition is key is required to be in the 'where' clause of the query to be able to locate the correct partition effectively.

5. Why is data duplication common in Cassandra?
Unlike relational databases, Cassandra does not rely on joins. In stark contrast, the same data gets duplicated across multiple query-specific tables to ensure that the reads are predictable and fast. Thus, data duplication is common in Cassandra.

6. Include a screenshot or copied output of:
        - SELECT * FROM plays_by_user WHERE user_id = 'u1';
        - SELECT * FROM plays_by_song WHERE song_id = 's1';

cqlsh:music_lab> SELECT * FROM plays_by_user WHERE user_id = 'u1';

 user_id | played_at                       | song_id | artist        | device | title
---------+---------------------------------+---------+---------------+--------+-----------------
      u1 | 2026-05-01 10:10:00.000000+0000 |      s3 | Billie Eilish | laptop |         bad guy
      u1 | 2026-05-01 10:05:00.000000+0000 |      s2 |    The Weeknd | iphone | Blinding Lights
      u1 | 2026-05-01 10:00:00.000000+0000 |      s1 |  Taylor Swift | iphone |       Anti-Hero

cqlsh:music_lab> SELECT * FROM plays_by_song WHERE song_id = 's1';

 song_id | played_at                       | user_id | artist       | device  | title
---------+---------------------------------+---------+--------------+---------+-----------
      s1 | 2026-05-01 12:00:00.000000+0000 |      u3 | Taylor Swift |  laptop | Anti-Hero
      s1 | 2026-05-01 11:00:00.000000+0000 |      u2 | Taylor Swift | android | Anti-Hero
      s1 | 2026-05-01 10:00:00.000000+0000 |      u1 | Taylor Swift |  iphone | Anti-Hero

cqlsh:music_lab> SELECT * FROM plays_by_user WHERE user_id = 'u1' AND played_at > '2026-05-01 10:05:00';
 user_id | played_at                       | song_id | artist        | device | title
---------+---------------------------------+---------+---------------+--------+---------
      u1 | 2026-05-01 10:10:00.000000+0000 |      s3 | Billie Eilish | laptop | bad guy

7. Submit the two exported CSV files:
        - plays_by_user.csv
        - plays_by_song.csv
