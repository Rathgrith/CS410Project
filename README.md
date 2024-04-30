### How to run the Project ###

# Step 1: DB Setup
1. `cd server/db`
2. `python 001_add_session_tables.py`
3. `python 002_add_interaction_table.py`
4. Download these 6 data files from https://uofi.app.box.com/s/m8lwwym09tay04669idbscphrsmt6w1e
  - all_papers_order.json
  - compressed_array.npz
  - docs_per_user.json
  - nn_model.pkl
  - normalized_user_ratings.json
  - quick_lookup.csv
5. Download arxiv-metadata-oai-snapshot.json from https://www.kaggle.com/datasets/Cornell-University/arxiv
  - First, download archive.zip, then extract to get the json file.
6. Place all the previous downloaded files in db folder
7. `python create_fresh_db.py` # See Note1

# Step 2: Start server process
1. `cd ..` # go to server folder
2. Install python if pip doesn't work
3. `pip install fastapi faiss-cpu sentence_transformers uvicorn`
4. `python server.py` # Running the backend server

# Step 3: UI 
1. `cd ../ui`
2. Install nodejs if npm doesn't work
3. `npm install`
4. `npm start` # Running the web server


# To Run
After set up: Run UI, run server.
Interact via webpage at http://localhost:3000

# Note1:
run: create_fresh_db.py
If you want to make the full DB (2M papers), set EARLY_STOP = -1
Else: set it to whatever number of papers you want to process.
If you had made the DB earlier, to update it with the new changes, simply run 001_add_session_tables.py to add the new tables. Otherwise, if you do not have a previous DB, create_fresh_db.py should be all you need to set up.



