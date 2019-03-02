import express from 'express';
import path from 'path';
import firebase from 'firebase-admin';

// Fetch the service account key JSON file contents
import config from './keys.json';
import bodyParser from 'body-parser';

// state variables
var songs: any;
var song: any;
var userId: any;

// setup for firebase real-time database
firebase.initializeApp({
  credential: firebase.credential.cert(config),
  databaseURL: 'https://amida-4242.firebaseio.com'
});

var db = firebase.database();

// get song list
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
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// routes
app.post('/login', function (req, res) { 	
  userId = req.body.id;
  res.redirect('/song-list');
});

app.get('/song-list', function (req, res) {
  res.render('song-list.ejs', { songs });  
});

app.get('/mixer/:id', function (req, res) {

  db.ref("songs/" + `${parseInt(req.params.id) - 1}`)
    .once("value", function(snapshot) {
      var data = {
        "song" : snapshot.val(),
        "userId" : userId
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
      res.status(204).send(); 
  });

});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});