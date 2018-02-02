# Rain-forcast
Rain-forcast is a messenger  chatbot tells you when to rain.

## Install Dependencies
* `yarn`
* `pip3 install -r requires.txt`

## Run Forecast without chatbot and ssl
* `cp config.json.example config.json` and write down your configuration (ignore tokens and ssl)
* `mkdir pub image ` 
* `node server.js`

## Run Forecast

### Setup 
* put your key & crt of ssl into your project
* `cp config.json.example config.json` and write down your configuration
* `mkdir pub image ` 
* create a facebook fan page
* Go to facebook for developer: https://developers.facebook.com/, see **Facebook Developer Setup**

### Facebook Developer Setup
* add a new messenger app
* create pageToken at Token Generation
* set webhookToken at Webhooks
* select a page to subscribe your webhook to the page event

### Run
* `node server.js`

## Test

### Setup
* setup testdata and modify config.json

### Run
* `python3 test.py YYYYMMDDHHmm YYYYMMDDHHmm x y`
