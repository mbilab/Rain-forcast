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
app.use(express.static(__dirname + config.path_save)) //! put into config.json

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

;(async () => { // fetch cwb images
//why there is no return befor Promise?
  const fetchImage = (time, verbose=false) => new Promise((resolve, reject) => { // {{{
    const fname = `CV1_3600_${dateAndTime.format(time, 'YYYYMMDDHHmm')}.png`
    const path = `${config.cwbPath}/${fname}`

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
      await fetchImage(time).then(() => analysis(time))
      console.log(`${dateAndTime.format(time, 'YYYYMMDDHHmm')} successed, next image in ${config.cwbSuccessTimeout / 60000} minute`)
      time = dateAndTime.addMinutes(time, 10)
      setTimeout(fetchService, config.cwbSuccessTimeout)
    } catch(e) {
      console.log(`${dateAndTime.format(time, 'YYYYMMDDHHmm')} failed, retry in ${config.cwbFailTimeout} minute`)
      setTimeout(fetchService, config.cwbFailTimeout)
    }
  } // }}}

  let time = new Date()
  time = dateAndTime.addMinutes(time, -parseInt(dateAndTime.format(time, 'mm')) % 10)
  await fetchImage(dateAndTime.addMinutes(time, -20), true)
  time = dateAndTime.addMinutes(time, -10)
  fetchService()
})()

function analysis(time) {
  execFile('python3', [
    `rain.py`,
    `${date.format(date.addMinutes(time, -10), 'YYYYMMDDHHmm').toString()}`,
    `${date.format(time, 'YYYYMMDDHHmm').toString()}`,
  ], (error, stdout, stderr) => {
    if (error) throw error
    console.log(stdout)
    if (ssl() && stdout[0] == "T") {
      url = `${config.imageHosting}prediction_${date.format(time, 'YYYYMMDDHHmm').toString()}.png`,
      getSubscribedUsers().then((users) => {for (const user of users) {
        callsendAPI('NON_PROMOTIONAL_SUBSCRIPTION', user.user_id, {
          "attchment":{
            "type":"image",
            "payload":{
              "url":url,
              "is_reusable":true
            }
          }
        })
      }})
    }
  })
}
