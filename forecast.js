const bodyParser = require('body-parser')
const date = require('date-and-time')
const { execFile } = require('child_process')
const express = require('express')
const fs = require('fs')
const http = require('http')
const https = require('https')
const request = require('request')
const config = require('./config')

const app = express()
////////////ssl certifacate//////////////
const options = {
  ca : fs.readFileSync('./ssl/ca_bundle.crt'),
  key: fs.readFileSync('./ssl/private.key'),
  cert: fs.readFileSync('./ssl/certificate.crt')
}

app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())
app.use(express.static(__dirname+'/pub'))

https.createServer(options, app).listen(config.port, () => {
  console.log(`listen on port:${config.port}`)
})

function analyze() {
  execFile('python3', [
    'rain.py',
    `${date.format(date.addMinutes(time, -10), 'YYYYMMDDHHmm').toString()},${date.format(time, 'YYYYMMDDHHmm').toString()},1675,1475`
  ], (error, stdout, stderr) => {
    if (error) {
      throw error
    }

    console.log(stdout)
    if (stdout[0] == "T") {
      let output = stdout.split('@')
      let filename = output[1]
      getSubscribedUsers().then((users) => {
        for (const user of users) {
          sendTextMessage(user.user_id, stdout)
          sendTextMessage(user.user_id, config.imageHosting + filename)
          sendPhotoMessage(user.user_id, config.imageHosting + filename)
        }
      })
    }
  })
}

////////download radar
let now = new Date()
let minutes_offset = (-1) * parseInt(date.format(now, 'mm')) % 10
let time = date.addMinutes(now,minutes_offset)
time = date.addMinutes(time, -20)

let filename = `image/CV1_3600_${date.format(time, "YYYYMMDDHHmm").toString()}.png`
let url = `http://www.cwb.gov.tw/V7/observe/radar/Data/HD_Radar/CV1_3600_${date.format(time, 'YYYYMMDDHHmm').toString()}.png`
console.log(`firtdownloading from: ${url}`)
http.get(url, function(response) {
  if(response.statusCode != 200) {
    return console.log(`Download failed.statusCode:${response.statusCode}`)
  }
  response.pipe(fs.createWriteStream(filename)).on('close', () => {
    time = date.addMinutes(time,10)
  })
})

setInterval(() => {
   filename = `image/CV1_3600_${date.format(time, "YYYYMMDDHHmm").toString()}.png`
   url = `http://www.cwb.gov.tw/V7/observe/radar/Data/HD_Radar/CV1_3600_${date.format(time, 'YYYYMMDDHHmm').toString()}.png`
  console.log(`downloading from: ${url}`)
  http.get(url, function(response) {
    if(response.statusCode != 200) {
      return console.log(`Download failed.statusCode:${response.statusCode}`)
    }
    response.pipe(fs.createWriteStream(filename)).on('close', () => {
      analyze()
      time = date.addMinutes(time,10)
    })
  })
}, 60000)
