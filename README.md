# Summary & use case:
This repo is an automated process to communicate from your terminal to google-sheets and clickup.\
This is intended for the purpose of tracking a list of sites.\
This will keep track of any status changes across syncing both clickup and google-sheets from the terminal.\
The user will have to follow instructions on the terminal and input status changes from there.\

##### Required Python Modules

##Google\
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

## Getting Started
### Credentials & Keys
Once the repo is cloned make sure to have the following available
- Clickup API Token (pk_XXXXXXXX)
- Google API JSON Key (place this in Keys Directory)
- Google Sheet ID (located in url of the google-sheet)
  - Note: make sure Sheet is Sharable via link
- Google Sheet Template name (A tab with a template for each new month created)

### Terminal Execution
Begin by pasting the following
```bash
cd nls-maintenance
python3 main.py
```
From here you should check to make sure your google and clickup credentials work correctly by selecting\
the first and second options.

### Using Selenium:
Within the Selenium directory you must execute the python script and have the .env variable ready with the credentials.