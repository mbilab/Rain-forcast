#!/usr/bin/env node

const bodyParser = require('body-parser')
const date = require('date-and-time')
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
  app.listen(config.port, () =>
    console.log (`listen on port: ${config.port} without ssl`)
  )
}

const fetchImage = time => new Promise((resolve, reject) => {
  const fname = `CV1_3600_${date.format(time, 'YYYYMMDDHHmm')}.png`
  const path = `${config.cwb_path}/${fname}`

  if (fs.existsSync(path)) {
    console.log(`${fname} exists, skip fetch`)
    return resolve()
  }

  const url = `http://www.cwb.gov.tw/V7/observe/radar/Data/HD_Radar/${fname}`
  console.log(`fetching ${fname}`)
  http.get(url, (response) => {
    if (200 != response.statusCode) {
      console.log(`fetch ${fname} failed`)
      return reject()
    }
    response.pipe(fs.createWriteStream(path).on('close', () => {
      console.log(`${fname} fetched`)
      resolve()
    }))
  })
})

////////download radar
let time = new Date()
time = date.addMinutes(time, -parseInt(date.format(time, 'mm')) % 10)
fetchImage(date.addMinutes(time, -20))
  //.then(() => time = date.addMinutes(time, 10))
  .then(() => console.log('ok'))
  .catch()

// setInterval(() => {
//    filename = `image/CV1_3600_${date.format(time, "YYYYMMDDHHmm").toString()}.png`
//    url = `http://www.cwb.gov.tw/V7/observe/radar/Data/HD_Radar/CV1_3600_${date.format(time, 'YYYYMMDDHHmm').toString()}.png`
//   console.log(`downloading from: ${url}`)
//   http.get(url, function(response) {
//     if(response.statusCode != 200) {
//       return console.log(`Download failed.statusCode:${response.statusCode}`)
//     }
//     response.pipe(fs.createWriteStream(filename)).on('close', () => {
//       analyze()
//       time = date.addMinutes(time,10)
//     })
//   })
// }, 1000 * 60)

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
