const bodyParser = require('body-parser')
const date=require('date-and-time');
const { execFile } = require('child_process');
const express = require('express');
const fs = require('fs');
const http = require('http');
const https = require('https')
const request = require('request');
const config = require('./config');
//db
const sqlite3 = require('sqlite3').verbose();    
const db = new sqlite3.Database('weather.db3');  

const app = express();
////////////ssl certifacate//////////////
const options = {
  ca : fs.readFileSync('./ssl/ca_bundle.crt'),
  key: fs.readFileSync('./ssl/private.key'),
  cert: fs.readFileSync('./ssl/certificate.crt')
};

app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())
//create server and pub dir
app.use(express.static(__dirname+'/pub'));
https.createServer(options, app).listen(config.port,()=>{
  console.log(`listen on port:${config.port}`)
})
// facebook api webhook
app.get('/webhook', function(req, res) {
  if (req.query['hub.mode'] === 'subscribe' && req.query['hub.verify_token'] === config.webhookToken) {
    console.log("Validating webhook");
    res.status(200).send(req.query['hub.challenge']);
  } else {
    console.error("Failed validation. Make sure the validation tokens match.");
    res.sendStatus(403);
  }
});
app.post('/webhook', function (req, res) {
    // Make sure this is a page subscription
    if (req.body.object === 'page') {

      // Iterate over each entry - there may be multiple if batched
      req.body.entry.forEach(function(entry) {
        // Iterate over each messaging event
        entry.messaging.forEach(function(event) {
          if (event.message) {
            receivedMessage(event);
          } else {
            console.log("Webhook received unknown event: ", event);
          }
        });
      });

      // Assume all went well.
      //
      // You must send back a 200, within 20 seconds, to let us know
      // you've successfully received the callback. Otherwise, the request
      // will time out and we will keep trying to resend.
      res.sendStatus(200);
    }
});

function sendTextMessage(recipientId, messageText) {
  callSendAPI({
    recipient: {
      id: recipientId
    },
    message: {
      text: messageText
    }
  });
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
  });
}
function callSendAPI(messageData) {
  request({
    uri: 'https://graph.facebook.com/v2.6/me/messages',
    qs: {access_token: config.pageToken },
    method: 'POST',
    json: messageData
  }, function (error, response, body) {
    if (!error && response.statusCode == 200) {
      console.log("Successfully sent generic message with id %s to recipient %s", body.message_id, body.recipient_id);
    } else {
      console.error("Unable to send message.");
      console.error(response);
      console.error(error);
    }
  });
}
//receive command and reply
function receivedMessage(event) {
  const senderID = event.sender.id;
  const recipientID = event.recipient.id;
  const timeOfMessage = event.timestamp;
  const message = event.message;
 
  console.log("Received message for user %d and page %d at %d with message:", senderID, recipientID, timeOfMessage);
  console.log(JSON.stringify(message));

  const messageId = message.mid;
  const messageText = message.text;
  const messageAttachments = message.attachments;
  //find user status
  getSenderStatus(senderID,(senderStatus)=>{
    if ( senderStatus == -1){
      if (messageText) {
        switch (messageText) {
          //user's command
          case '我要訂閱':
            sendTextMessage(senderID, "以後將帶給您即時的天氣預報");
          //update status
            db.run("INSERT INTO users VALUES ( $user_id , $user_status )",{
              $user_id : senderID,
              $user_status : 1 ,
            })
            break;
          default:
            sendTextMessage(senderID, "Hi!請輸入'我要訂閱'，若成大要下雨時,便會通知您 ");
        }
      }else if (messageAttachments) {
        sendTextMessage(senderID, "(隨機貼圖)");
      }   
    }
    else if ( senderStatus == 0 ){
      if (messageText) {
        switch (messageText) {
          //user's command
          case '我要訂閱':
            sendTextMessage(senderID, "感謝乾爹再次訂閱，依然為乾爹提供最即時的降雨預報。");
            //update status
            db.run("UPDATE users SET user_status = $user_status WHERE user_id = $user_id", {
              $user_id : senderID,
              $user_status : 1 , 
            })
            break;
          default:
            sendTextMessage(senderID, "Hi!請輸入'我要訂閱'，若成大要下雨時,便會通知您 ");
        }
      }else if (messageAttachments) {
        sendTextMessage(senderID, "(隨機貼圖)");
      }   
    }
    else if(senderStatus == 1){
      if (messageText) {
        switch (messageText) {
          //user's command
          case '取消訂閱':
            sendTextMessage(senderID, "ＱＱ");
            //update status
            db.run("UPDATE users SET user_status = $user_status WHERE user_id = $user_id", {
                $user_id  : senderID,
                $user_status : 0  , 
            });
            break;
          default:
            sendTextMessage(senderID, "安安～,～暫時不提供聊天服務喔！若要取消訂閱，請輸入'取消訂閱'。");
        }
      } else if (messageAttachments) {
        sendTextMessage(senderID, "(隨機貼圖)");
      }   
    }
  })
}
//sqlite api(?
function getUsers (callback){//getUsers((Users)=>{}) ; 
    db.all("SELECT * FROM users" ,(err,rows)=> callback(rows) )
}
function getSenderStatus(senderID,callback){
  var rowProcessed = 0 ;
  var senderStatus = -1 ;
  getUsers((users)=>{
    users.forEach((row,index,array)=>{
       if(row.user_id == senderID ){
         senderStatus = row.user_status;
       }
       rowProcessed++;
       if ( rowProcessed === array.length ){
         callback(senderStatus);
       }
     })
  })
}


function analyze(){
  execFile('python', ['rain.py',date.format(date.addMinutes(time,-10),'YYYYMMDDHHmm').toString()+','+date.format(time,'YYYYMMDDHHmm').toString()+',1675,1475'], (error, stdout, stderr) => {
    if (error) {
      throw error;
    }
    console.log(stdout);
    if(stdout[0]=="T"){
      var output = stdout.split('@')
      var filename = output[ 1 ]
      getUsers (( Users )=>{
        Users.forEach(( User , index , array )=>{
          getSenderStatus( User.user_id ,( senderStatus )=>{
            if( senderStatus ){
              sendTextMessage( User.user_id , stdout );
              sendTextMessage( User.user_id , config.imageHosting + filename );
              sendPhotoMessage(User.user_id , config.imageHosting + filename );
            }
          })
        })
      })
    }
  });
}

/*
function analyze(){
  execFile('python', ['rain.py','10,11,1675,1475'], (error, stdout, stderr) => {
    if (error) {
      throw error;
    }
    console.log(stdout);
    if(stdout[0] == "T"){
      var output = stdout.split('@')
      var filename = output[ 1 ]
      getUsers (( Users )=>{
        Users.forEach(( User , index , array )=>{
          getSenderStatus( User.user_id ,( senderStatus )=>{
            if( senderStatus ){
              sendTextMessage( User.user_id , stdout );
              sendTextMessage( User.user_id , "https://luffy.ee.ncku.edu.tw:20000/" + filename );
              sendPhotoMessage(User.user_id , "https://luffy.ee.ncku.edu.tw:20000/" + filename );
            }
          })
        })
      })
    }
  });
}
*/

////////download radar
let now=new Date();
let minutes_offset=(-1)*parseInt(date.format(now,'mm'))%10;
let time=date.addMinutes(now,minutes_offset);
time=date.addMinutes(time,-10);

setInterval(()=>{
  const filename="image/CV1_3600_"+date.format(time,"YYYYMMDDHHmm").toString()+".png";
  const url="http://www.cwb.gov.tw/V7/observe/radar/Data/HD_Radar/CV1_3600_"+date.format(time,'YYYYMMDDHHmm').toString()+".png"
  console.log("downloading from:"+url);
  http.get(url, function(response) {
    if(response.statusCode != 200) {
      return console.log(`Download failed.statusCode:${response.statusCode}`);
    }
    response.pipe(fs.createWriteStream(filename)).on('close', () => {
      analyze();
      time = date.addMinutes(time,10);
    });
  });
},60000)


