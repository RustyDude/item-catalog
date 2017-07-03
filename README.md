# Project: Item Catalog

A **Flask API Project**, demonstrating a CRUD operations of mock-up item catalog application using **Sqlachemly** and **Google Oauth** for registration and authentication system. Logged in user has to ability to manipulate their own items.

## Requirements

* [Vagrant](https://www.vagrantup.com/downloads.html)
* [Virtual Machine](https://www.virtualbox.org/wiki/Downloads)
* [Google Account](https://www.gmail.com)

## Get it started.

### Setting up Google Login
To get the Google login working there are a few additional steps:

* Go to [Google Dev Console](https://console.developers.google.com)
* Sign up or Login if prompted
* Go to Credentials
* Select Create Crendentials > OAuth Client ID
* Select Web application and Enter name 'Item-Catalog'
* Set Authorized JavaScript origins = 'http://localhost:5000'
* Set Authorized redirect URIs = 'http://localhost:5000/login' && 'http://localhost:5000/gconnect'
* Once finish creating, Copy the Client ID and paste it into the `data-clientid` in header.html
* On the Dev Console Select Download JSON and rename it to client_secrets.json or you may manually change the data on the already setup clients_secrets.json
* Place JSON file in item-catalog directory that you cloned from here._(overwrite the previous one)_

### Setting up VM configuration

* Download and unzip [FSND-Virtual-Machine.zip](https://d17h27t6h515a5.cloudfront.net/topher/2017/May/59125904_fsnd-virtual-machine/fsnd-virtual-machine.zip). Alternately, you can use Github to fork and clone the repository https://github.com/udacity/fullstack-nanodegree-vm.

### Downloading a copy
* **Fork** the [repository](https://github.com/RustyDude/item-catalog). _(You may fork or not totally up to you)_

* Once you have your own repository. **You may click Clone or download**, then using _HTTPs section_ copy clone URL. (Put it inside your vagrant subdirectory)

### Start the virtual machine

* Once inside the vagrant subdirectory, run the command:
```vagrant up```

* Upon installation, run this command to log you inside the VM.
```vagrant ssh```

### Set up the database
* Go inside item_catalog directory. now you should have a file called "_**db_setup.py**_"
* In terminal run this command:
```python db_setup.py```

### Running the item catalog application
* Run this command:
``` python application.py```

## JSON serialized data
* Catalog Categories: `/catalog/categories/JSON` - Shows all category
* Category Items: `/catalog/<string:category>/JSON` - Shows all item on a specific category
* Singe Item: `/catalog/<string:category>/<string:item/JSON` - Shows a specific item in a category

Nanodegree Course courtesy of [Udacity](https://www.udacity.com/).