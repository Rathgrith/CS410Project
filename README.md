# UI
## Set up
npm install react-router-dom axios
## To run
npm start

# DB
## To set up
Just do this once.
run: create_fresh_db.py
If you want to make the full DB (2M papers), set EARLY_STOP = -1
Else: set it to whatever number of papers you want to process.
If you had made the DB earlier, to update it with the new changes, simply run 001_add_session_tables.py to add the new tables. Otherwise, if you do not have a previous DB, create_fresh_db.py should be all you need to set up.

# Server
## To set up
Install what it says is missing until everything is installed :)
## To run
python server.py