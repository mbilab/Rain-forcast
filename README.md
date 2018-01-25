# Rain-forcast
Rain-forcast is a messenger  chatbot tells you when to rain.

## Setup
* `cp config.json.example config.json` and write dwon your configuration
* `mkdir pub`,`mkdir image`and  build folders 
* put your key & crt of ssl into ssl file

## Build
* create a facebook fan page  
```
Go to facebook for developer: https://developers.facebook.com/
```
* add a new messenger app
* create pageToken at Token Generation
* set webhookToken at Webhooks
* select a page to subscribe your webhook to the page event

## Run
* `node server.js`

