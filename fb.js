const sqlite3 = require('sqlite3').verbose()
const db = new sqlite3.Database('weather.db')
const reply = require('./reply.json')
const request = require('request')
const config = require('./configtest')

const self = module.exports = {
  webhook_get : function(req, res) {
      if (req.query['hub.mode'] === 'subscribe' && req.query['hub.verify_token'] === config.webhookToken) {
        console.log("Validating webhook")
        res.status(200).send(req.query['hub.challenge'])
      } else {
        console.error("Failed validation. Make sure the validation tokens match.")
        res.sendStatus(403)
      }
    },

  webhook_post : function(req, res) {
    // Make sure this is a page subscription
    if (req.body.object === 'page') {
      // Iterate over each entry - there may be multiple if batched
      req.body.entry.forEach(function(entry) {
        // Iterate over each messaging event
        entry.messaging.forEach(function(event) {
          if (event.message) {
            self.receivedMessage(event)
          } else {
            console.log("Webhook received unknown event: ", event)
          }
        })
      })
      res.sendStatus(200)
    }
  },


  callSendAPI : function (type, recipientId, respone) {
    let messageData = {
      messaging_type : type,
      recipient : {
        id : recipientId
      },
      message : respone
    }

    request({
      uri: 'https://graph.facebook.com/v2.6/me/messages',
      qs: { access_token: config.pageToken },
      method: 'POST',
      json: messageData
    }, (error, response, body) => {
      if (!error && response.statusCode == 200) {
        console.log("Successfully sent generic message with id %s to recipient %s", body.message_id, body.recipient_id)
      } else {
        console.error("Unable to send message.")
        console.log(respone)
      }
    })
  },

  //receive command and reply
  receivedMessage : function(event) {
    const senderID = event.sender.id
    const { mid: messageId, text: messageText, attachments: messageAttachments } = event.message

    console.log("Received message for user %d and page %d at %d with message:", senderID, event.recipient.id, event.timestamp)
    console.log(JSON.stringify(event.message))

    let type ='RESPONSE'
    //find user status
    self.getSenderStatus(senderID).then((senderStatus) => {
      if (messageText) {
        const text = reply[senderStatus].text.filter(el => el.q === messageText)
        let response = reply[senderStatus].default
        if (text.length) {
          response = text[0].a
          self.dispatchDBAction(senderID, senderStatus)
        }
        self.callSendAPI(type, senderID, response)
      } else if (messageAttachments) {
        self.callSendAPI(type, senderID, {"text" : "^.^"})
      }
    })
  },

  dispatchDBAction : function (id, status) {
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
  },

  //sqlite api(?

  getUser : (userID) => new Promise((resolve, reject) => {
    db.all("SELECT * FROM users WHERE user_id = $user_id", { $user_id: userID } ,(err, rows) => {
      if (rows.length == 1) {
        resolve(rows[0])
      } else {
        resolve()
      }
    })
  }),

  getSubscribedUsers : () => new Promise((resolve, reject) => {
    db.all("SELECT * FROM users WHERE user_status = 1" ,(err, rows) => resolve(rows))
  }),

  getSenderStatus : (userID) => self.getUser(userID).then(user => user ? user.user_status : -1),
 
}
