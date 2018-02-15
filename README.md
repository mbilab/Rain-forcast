# Rain-forcast
Rain-forcast is a messenger  chatbot tells you when to rain.

## Install Dependencies
* `yarn`
* `pip3 install -r requires.txt`

## Run Forecast without chatbot and ssl
* `cp config.sample.json config.json` and write down your configuration (ignore tokens and ssl)
* `mkdir fetch result`we put image downloaded in `fetch` and result of rain.py in `reslt`
* `node server.js`

## Run Forecast

### Setup
* put your key & crt of ssl into your project
* `cp config.sample.json config.json` and write down your configuration
* `mkdir fetch result`we put image downloaded in fetch and `result` of rain.py in `reslt`
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

### Run
* `python3 rain.py 00 01 1675 1475` # True
* `python3 rain.py 10 11 1675 1475` # True
* Outputs should be true with images:`prediction_01.png` or `prediction_11.png` in `pub/`
