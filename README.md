# Collect-Atlan

GitHub Repository Link : https://github.com/khatryshikha/SocialCops-Django

## Introduction 

Atlan Internship Challenge - Backend

Main Technologies/Tools Used:
  - Python 3.6
  - Django
  - Celery
  - Redis
  - Sqlite
  - Gunicorn
  - HTML/JavaScript
  
## Run the production build of project in Docker Container
Make sure you have [Docker](https://docs.docker.com/installation/) and [docker-compose](http://docs.docker.com/compose/install/) installed in your system.
  1. Clone the project
  `git clone https://github.com/anuragiiits/Collect-Atlan.git`
  2. Move to project folder 
  `cd Collect-Atlan`
  3. Run `docker-compose up --build` and wait for Docker to set up the container and start the server.
  4. Open `http://127.0.0.1:8080/` in your browser to open the app
  
## Installation Instructions (Make sure you have Python 3, Redis server and virtual environment installed)
  1. Clone the project
  `git clone https://github.com/anuragiiits/Collect-Atlan.git`
  2. Move to project folder 
  `cd Collect-Atlan`
  3. Create your virtual environment 
  `virtualenv venv`
  4. Activate the virtual environment 
  `source venv/bin/activate`
  5. Install the requirements for the Project
  `pip install -r requirements.txt`
  6. Open `Collect/settings.py`  
    * Uncomment the commented SECRET_KEY, DEBUG and ALLOWED_HOSTS values and Comment the existing values which is set for Production Environment
    * Change the REDIS_BROKER_URL and REDIS_BACKEND_URL from `redis://redis:6379` to `redis://localhost:6379`
  7. Run the migrations
  `python manage.py makemigrations` and
  `python manage.py migrate`
  8. Run the server
  `python manage.py runserver`
  9. Open `http://127.0.0.1:8000/` in your browser
  
  ## Endpoints Usability
   1. **Endpoint for Upload CSV file**
   
   `http://127.0.0.1:8080/example1/`  
   Method: POST  
   Receives file with key as `csv_data`  
   This API starts uploading the CSV file to the SQLite database. The application also generates random date between 2000-01-01 and 2020-12-31 
   corresponding to each row of CSV data. This date is used as a filter in the 2nd Endpoint. You can also see the progress bar of the uploading process in the terminal.
   The Task ID is returned as the response in the webpage which can be used to stop this task.  
   
   ![Progress Bar: Uploading CSV](https://github.com/anuragiiits/Collect-Atlan/blob/master/Screenshots/Task%20Running.png)
  
   Note: A `testing_data.csv` file is present in root directory that can be used to check this example task.
   
   
  2. **Endpoint for Exporting Data based on Date Filter**
   
   `http://127.0.0.1:8080/example2/`  
   Method: POST  
   Receives `start_date` and `end_date` in `YYYY-MM-DD` format  
   This API starts exporting the data from the SQLite database in a CSV file. You can see the progress bar of the downloading process in the terminal.
   The Task ID is returned as the response in the webpage which can be used to stop this task.  
   
   ![Progress Bar: Exporting CSV](https://github.com/anuragiiits/Collect-Atlan/blob/master/Screenshots/Task%20Running.png)
   
   NOTE: Please run the 1st Endpoint successfully before running the 2nd Endpoint to see some result. This is because the data imported from 
   the CSV file in 1st API is stored in the database and used by 2nd API during exporting of data based on start date and end date. As mentioned above, 
   the start date and end date is randomly created along with the uploaded data in 1st endpoint in order to use that field for the 2nd API.
  
  
  3. **Endpoint to Stop a Task**
   
   `http://127.0.0.1:8080/stop/<task_id>/`  
   Method: GET  
   Receives `task_id` in the Endpoint URL  
   This API stops the task from the execution if the task hasn't finished yet.  
   It also keeps the database consistent by removing any changes made in the database by a stopped task during its processing.  
   ![Exporting Stopped](https://github.com/anuragiiits/Collect-Atlan/blob/master/Screenshots/Task%20Stopped.png)
  
  
  4. **Endpoint to Check the status of Export Process initiated by 2nd API**
   
   `http://127.0.0.1:8080/poll_for_download/<task_id>/?filename=<filename>`  
   Method: GET  
   Receives `task_id` in the Endpoint URL with Optional query parameters as key-value pair  
   This API is used by the Frontend script to poll in every 5 seconds if the export task running in background is finished yet.
   If the export(background task processing) is finished, the filename parameter is used to download the file with the exported data.

  
