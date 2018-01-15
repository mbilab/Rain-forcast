const bodyParser = require('body-parser')
const date = require('date-and-time')
const { execFile } = require('child_process')
const express = require('express')
const fs = require('fs')
const http = require('http')
const https = require('https')
const request = require('request')
const config = require('./config')
const reply = require('./reply.json')
// db
const sqlite3 = require('sqlite3').verbose()
const db = new sqlite3.Database('weather.db')

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

// facebook api webhook
app.get('/webhook', function(req, res) {
  if (req.query['hub.mode'] === 'subscribe' && req.query['hub.verify_token'] === config.webhookToken) {
    console.log("Validating webhook")
    res.status(200).send(req.query['hub.challenge'])
  } else {
    console.error("Failed validation. Make sure the validation tokens match.")
    res.sendStatus(403)
  }
})

app.post('/webhook', function (req, res) {
    // Make sure this is a page subscription
    if (req.body.object === 'page') {

      // Iterate over each entry - there may be multiple if batched
      req.body.entry.forEach(function(entry) {
        // Iterate over each messaging event
        entry.messaging.forEach(function(event) {
          if (event.message) {
            receivedMessage(event)
          } else {
            console.log("Webhook received unknown event: ", event)
          }
        })
      })

      // Assume all went well.
      //
      // You must send back a 200, within 20 seconds, to let us know
      // you've successfully received the callback. Otherwise, the request
      // will time out and we will keep trying to resend.
      res.sendStatus(200)
    }
})

function sendTextMessage(recipientId, messageText) {
  callSendAPI({
    recipient: {
      id: recipientId
    },
    message: {
      text: messageText
    }
  })
}

function sendPhotoMessage(recipientId, photoUrl) {
  console.log(`${photoUrl}`)
  callSendAPI({
    recipient: {
      id: recipientId
    },
    message: {
      attachment: {
        type: "image",
        payload: {
          url: photoUrl,
          is_reusable: true
        }
      }
    }
  })
}
function callSendAPI(messageData) {
  request({
    uri: 'https://graph.facebook.com/v2.6/me/messages',
    qs: { access_token: config.pageToken },
    method: 'POST',
    json: messageData
  }, function (error, response, body) {
    if (!error && response.statusCode == 200) {
      console.log("Successfully sent generic message with id %s to recipient %s", body.message_id, body.recipient_id)
    } else {
      console.error("Unable to send message.")
      console.error(response)
      console.error(error)
    }
  })
}

function dispatchDBAction(id, status) {
  switch (status) {
    case -1:
      db.run("INSERT INTO users VALUES ($user_id , $user_status )", { $user_id : id, $user_status : 1 })
      break
    case 0:
      db.run("UPDATE users SET user_status = $user_status WHERE user_id = $user_id", { $user_id : id, $user_status : 1 })
      break
    case 1:
      db.run("UPDATE users SET user_status = $user_status WHERE user_id = $user_id", { $user_id  : id, $user_status : 0 })
      break
    default:
      throw new Error("Unknown sender status: " + status + ", sender id: " + id)
  }

}

//receive command and reply
function receivedMessage(event) {
  const senderID = event.sender.id
  const { mid: messageId, text: messageText, attachments: messageAttachments } = event.message

  console.log("Received message for user %d and page %d at %d with message:", senderID, event.recipient.id, event.timestamp)
  console.log(JSON.stringify(event.message))

  //find user status
  getSenderStatus(senderID).then((senderStatus) => {

    if (messageText) {
      const text = reply[senderStatus].text.filter(el => el.q === messageText)
      let response = reply[senderStatus].default
      if (text.length) {
        response = text[0].a
        dispatchDBAction(senderID, senderStatus)
      }
      sendTextMessage(senderID, response)
    } else if (messageAttachments) {
      sendTextMessage(senderID, "(隨機貼圖)")
    }
  })
}
//sqlite api(?
const getUsers = () => new Promise((resolve, reject) => {
  db.all("SELECT * FROM users" ,(err, rows) => resolve(rows))
})

const getUser = (userID) => new Promise((resolve, reject) => {
  db.all("SELECT * FROM users WHERE user_id = $user_id", { $user_id: userID } ,(err, rows) => {
    if (rows.length == 1) {
      resolve(rows[0])
    }
    else {
      resolve()
    }
  })
})

const getSubscribedUsers = () => new Promise((resolve, reject) => {
  db.all("SELECT * FROM users WHERE user_status = 1" ,(err, rows) => resolve(rows))
})

const getSenderStatus = (senderID) => getUser(snderID).then(user => user ? user.user_status : -1)

function analyze() {
  execFile('python', [
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

