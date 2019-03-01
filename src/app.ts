import express from 'express';
import path from 'path';
var admin = require('firebase-admin');

// Fetch the service account key JSON file contents
import config from './keys.json';

admin.initializeApp({
  credential: admin.credential.cert(config),
  databaseURL: 'https://amida-4242.firebaseio.com'
});

// As an admin, the app has access to read and write all data, regardless of Security Rules
var db = admin.database();

let songs: any;
let data: any;

var ref = db.ref("songs");
ref.once("value", function(snapshot) {
  songs = snapshot.val();
});

// Create a new express application instance
const app: express.Application = express();

// set ejs as the view engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '/views'));

app.use(express.static(__dirname + '/public'));

app.get('/', function (req, res) {
  res.render('index.ejs', { });  
});

app.get('/login', function (req, res) {
  res.render('login.ejs', { });  
});

app.post('/login', function (req, res) {
  res.render('song-list.ejs', { songs });
})

app.get('/new-user', function (req, res) {
  res.render('index.ejs', { });  
});

app.get('/song-list', function (req, res) {
  res.render('song-list.ejs', { songs });  
});

app.get('/mixer/:id', function (req, res) {

  db.ref("songs/" + req.params.id)
    .once("value", function(snapshot) {
      data = {
        "song" : snapshot.val(),
        "userId" : "abc123"
      }
      console.log(data);
      res.render('mixer.ejs', { data });  
  });
});

app.get('/save/:userId/:songId/:bass/:drums/:other/:vocals', function (req, res) {

  console.log(req.params);

  var mix = {
    "id" : req.params.songId,
    "bass" : req.params.bass,
    "drums" : req.params.drums,
    "other" : req.params.other,
    "vocals" : req.params.vocals,
  }

  db.ref("users/" + req.params.userId + "/mixes/")
    .push(mix, function() {
      console.log(data);
      res.render('mixer.ejs', { data });  
  });

});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});