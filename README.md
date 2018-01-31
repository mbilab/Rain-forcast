# Rain-forcast
Rain-forcast is a messenger  chatbot tells you when to rain.

## Install Dependencies
* `yarn`
* `pip3 install -r requires.txt`

## Run Forecast without chatbot
* `node forecast.js`

## Run Forecast

### Setup 
* `cp config.json.example config.json` and write down your configuration
* `mkdir pub image ssl` 
* put your key & crt of ssl into `ssl` folder
* create a facebook fan page
* Go to facebook for developer: https://developers.facebook.com/, see **Facebook Developer Setup**

### Facebook Developer Setup
* add a new messenger app
* create pageToken at Token Generation
* set webhookToken at Webhooks
* select a page to subscribe your webhook to the page event

### Run
* `node server.js`

