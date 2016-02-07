# udadisi-web



## Installation
The miner is build using Python 2.7 and the [Flask framework](http://flask.pocoo.org/) and a bunch of other libraries.  Assuming you have an up-to-date Python 2.7 environment, the simplest way to install all the dependencies is to use pip and the requirements file that's in the repository.  The command is:

`pip install -r requirements.txt`

Following that you will need to install the NLTK stopwords corpus using the NTLK downloader.  Follow the instructions [here](http://www.nltk.org/data.html) to find out how to install corpora. 

The miner is then running by executing runserver.py using Python.

`python application`

## Usage
The miner is designed to be managed via the admin interface of the Udadisi engine.  It exposes the following API endpoints.

`GET  /categories` returns a html table listing all the categories currently availabily.

`POST /categories` takes a json object as a parameter in the post body.  Content-Type should be `application/json`.  The object should contain a single key named 'id' with an integer value.  This will create a new category with that array.

`GET /categories/<category_id` returns a form for viewing and editing the settings for the category.

`POST /categories/<category_id` processes the form and updates the settings for the category.  When the settings are saved the miner will begin mining that category.

`DELETE /categories/<category_id` stop the miner from mining that category and delete the category.

