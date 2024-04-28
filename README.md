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
There is a requirements.txt that should have everything/most of it.
## To run
python server.py

# To Run
After set up: Run UI, run server.
Interact via webpage at http://localhost:3000