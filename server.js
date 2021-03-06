#!/usr/bin/env node

const bodyParser = require('body-parser')
const config = require('./config')
const dateAndTime = require('date-and-time')
const {execFile} = require('child_process')
const express = require('express')
const fb = require('./fb')
const fs = require('fs')
const http = require('http')
const https = require('https')

const app = express()

app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())
app.use(express.static(__dirname + config.tmpPath))

// ssl certifacate
if (config.ssl) {
  var options = {
    ca: fs.readFileSync(config.ssl.ca),
    cert: fs.readFileSync(config.ssl.cert),
    key: fs.readFileSync(config.ssl.key),
  }

  https.createServer(options, app).listen(config.port, () => console.log(`listen on port:${config.port}`))

  app.get('/webhook', fb.webhook_get)
  app.post('/webhook', fb.webhook_post)
} else {
  app.listen(config.port, () => console.log (`listen on port: ${config.port} without ssl`))
}

const timeString = (time, minutes=0) => dateAndTime.format(dateAndTime.addMinutes(time, minutes), 'YYYYMMDDHHmm')

;(async () => { // fetch cwb images
  const fetchImage = (time, verbose=false) => new Promise((resolve, reject) => { // {{{
    const fname = `CV1_3600_${timeString(time)}.png`
    const path = `${config.cwb.path}/${fname}`

    if (fs.existsSync(path)) {
      if (verbose) console.log(`${fname} exists, skip fetch`)
      return resolve()
    }

    const url = `http://www.cwb.gov.tw/V7/observe/radar/Data/HD_Radar/${fname}`
    if (verbose) console.log(`fetching ${fname}`)
    http.get(url, (response) => {
      if (200 != response.statusCode) {
        if (verbose) console.log(`fetch ${fname} failed`)
        return reject(time)
      }
      response.pipe(fs.createWriteStream(path).on('close', () => {
        if (verbose) console.log(`${fname} fetched`)
        resolve()
      }))
    })
  }) // }}}

  const fetchService = async () => { // {{{
    try {
      await fetchImage(time)
      console.log(`${timeString(time)} successed, next image in ${config.cwb.successTimeout / 60000} minute`)
      if (config.ssl) analyze(time)
      time = dateAndTime.addMinutes(time, 10)
      setTimeout(fetchService, config.cwb.successTimeout)
    } catch(e) {
      console.log(`${timeString(time)} failed, retry in ${config.cwb.failTimeout / 60000} minute`)
      setTimeout(fetchService, config.cwb.failTimeout)
    }
  } // }}}

  let time = new Date()
  time = dateAndTime.addMinutes(time, -parseInt(dateAndTime.format(time, 'mm')) % 10)
  await fetchImage(dateAndTime.addMinutes(time, -10), true)
  fetchService()
})()

function analyze(time) {
  execFile('python3', [
    './rain.py',
    timeString(time, -10),
    timeString(time),
  ], (error, stdout, stderr) => {
    if (error) throw error
    console.log(stdout)
    if ('T' !== stdout[0]) return
    url = `${config.host}/prediction_${timeString(time)}.png` //! solve 'prediction_'
    //!fb.broadcast()
    fb.getSubscribedUsers().then((users) => {
      for (const user of users) {
        fb.callsendAPI('NON_PROMOTIONAL_SUBSCRIPTION', user.user_id, {
          // first parameter is message type which fb asks developers to add
          "attchment":{
            "type":"image",
            "payload":{
              "url":url,
              "is_reusable":true
            }
          }
        })
      }
    })
  })
}
