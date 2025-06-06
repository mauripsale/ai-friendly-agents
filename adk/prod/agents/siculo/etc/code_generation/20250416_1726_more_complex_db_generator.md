It works perfectly. Now I have to say, the test DB we've built so far is very small and silly. I would like to have a BIGGER DB with THREE tables, all interconnected with a foreign key, at least A <=> B <=> C , better if there are even more foreign ids. Lets make sure to use the RoR convetion (user_id, part_id) and so forth.



Since I work for Google, it would be nice to have something like:

* People, (name, id, email, ..)

attending

* Events (a googley name, location, date, ..)

and then I let you decide the 3rd column



I'd like to have a bash script to populate this and all tables should have a timestamp "created_at" and "updated_at", like in rails. Also among the 3 tables, i want all values represented: dates, floats, integers, strings, maybe ENUMs. finally I'd like to have some constraints, eg Unique email for user and unique (event_id, year) for events.



Generation should look similar to this but with new data and maybe with HERE comments, or maybe catting some sort of SQL population script, as you prefer. Maybe that'd be more readable

-----

{{ attached bin/create_sample_db.sh }}



## rev2

this is amazing but it fails

bin/sbrodola-google-events.sh

--- Preparing database: google_events.sqlite ---

    (Dropping existing tables/triggers if they exist)

Parse error near line 125: table events has no column named ticket_price

Runtime error near line 139: FOREIGN KEY constraint failed (19)

