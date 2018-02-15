#!/usr/bin/env node

const bodyParser = require('body-parser')
const dateAndTime = require('date-and-time')
const { execFile } = require('child_process')
const express = require('express')
const fs = require('fs')
const http = require('http')
const https = require('https')
const request = require('request')
const config = require('./config')
const fb = require('./fb')

const app = express()

app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())
app.use(express.static(__dirname + '/tmp')) //! put into config.json

// ssl certifacate
if (config.ssl) {
  var options = {
    ca : fs.readFileSync(config.ssl.ca),
    key: fs.readFileSync(config.ssl.key),
    cert: fs.readFileSync(config.ssl.cert)
  }

  https.createServer(options, app).listen(config.port, () => console.log(`listen on port:${config.port}`))

  app.get('/webhook',fb.webhook_get)
  app.post('/webhook',fb.webhook_post)

} else {
  // app.listen(config.port, () =>
  //   console.log (`listen on port: ${config.port} without ssl`)
  // )
}

////////////////////////////////////////////////////////////////////////////////
// fetch cwb images

const fetchImage = (time, verbose=false) => new Promise((resolve, reject) => { // {{{
  const fname = `CV1_3600_${dateAndTime.format(time, 'YYYYMMDDHHmm')}.png`
  const path = `${config.cwb_path}/${fname}`

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
    console.log(`${dateAndTime.format(time, 'YYYYMMDDHHmm')} successed, next image in 9 minute`)
    time = dateAndTime.addMinutes(time, 10)
    setTimeout(fetchService, 1000 * 60 * 9)
  } catch(e) {
    console.log(`${dateAndTime.format(time, 'YYYYMMDDHHmm')} failed, retry in 1 minute`)
    setTimeout(fetchService, 1000 * 10 * 1)
  }
} // }}}

let time = new Date()
;(async () => {
  time = dateAndTime.addMinutes(time, -parseInt(dateAndTime.format(time, 'mm')) % 10)
  await fetchImage(dateAndTime.addMinutes(time, -20), true)
  time = dateAndTime.addMinutes(time, -10)
  fetchService()
})()

// function analyze() {
//   execFile('python3', [
//     `rain.py`,
//     `${date.format(date.addMinutes(time, -10), 'YYYYMMDDHHmm').toString()}`,
//     `${date.format(time, 'YYYYMMDDHHmm').toString()}`,
//     `1675`,`1475`
//   ], (error, stdout, stderr) => {
//     if (error) {
//       throw error
//     }
//
//     console.log(stdout)
//     if (ssl()) {
//       if (stdout[0] == "T") {
//         let output = stdout.split('@')
//         let filename = output[1]
//         getSubscribedUsers().then((users) => {
//           for (const user of users) {
//             sendPhotoMessage(user.user_id, config.imageHosting + filename)
//           }
//         })
//       }
//     }
//   })
// }
