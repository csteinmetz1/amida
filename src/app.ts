import express from 'express';
import path from 'path';
import firebase from 'firebase-admin';

import bodyParser from 'body-parser';
import cookieParser from 'cookie-parser';
import session from 'express-session';

// Fetch the service account key JSON file contents
import config from './keys.json';
import { SSL_OP_SINGLE_DH_USE } from 'constants';

// setup for firebase real-time database
firebase.initializeApp({
  credential: firebase.credential.cert(config),
  databaseURL: 'https://amida-4242.firebaseio.com'
});

var db = firebase.database();

// Create a new express application instance
const app: express.Application = express();

// set ejs as the view engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '/views'));

app
  .use(express.static(__dirname + '/public'))
  .use(bodyParser.json())
  .use(bodyParser.urlencoded({ extended: true }))
  .use(cookieParser())
  .use(session({ secret: 'tk421', resave: false, saveUninitialized: true, }));

// routes
app.post('/login', function (req, res) { 	
  if (req.session) {
    db.ref("users").once("value", function(snapshot) {
      var users = snapshot.val();
      console.log(req.body.id, Object.keys(users));
      if (Object.keys(users).indexOf(req.body.id) < 0)
      {
        console.log(`User ${req.body.id} not found!`);
        var error = {"text" : `User id (${req.body.id}) not found.`}
        return res.render("login.ejs", error);
      }
      else
      {
        req.session.userId = req.body.id;
        // get songs from database and save
        db.ref("songs").once("value", function(snapshot) {
          req.session.songs = snapshot.val();
          return res.redirect('/song-list');
        });
      }
    })
  }
});

app.get('/login', function (req, res) { 	
  var error = {"text" : ""}
  return res.render("login.ejs", error);
});

app.get('/logout', function (req, res) { 	
  if (req.session) {
    req.session.destroy(function(err) {
      if (err) return console.log(err);
        return res.redirect('/');
    });
  }
});

app.post('/new-user', function (req, res) { 	
  if (req.session) {
    req.session.userId = req.body.id;
    var userData = {
      "id" : req.body.id,
      "experience" : req.body.experience,
      "playback" : req.body.playback,
    }
    db.ref("songs").once("value", function(snapshot) {
      req.session.songs = snapshot.val();
      res.redirect('/song-list');
    });
    db.ref("users/" + req.body.id)
      .set(userData, function() {
    });
  }
});

app.get('/song-list', function (req, res) {
  var data = {};
  data.userId = req.session.userId;
  data.songs = req.session.songs;
  data.mixes = [];

  db.ref("users/" + req.session.userId + "/mixes/")
    .once("value", function(snapshot) {
      if (snapshot.exists())
      {
        var mixes = new Set(Object.values(snapshot.val()).map(Number));
      }
      else
      {
        var mixes = new Set();
      }
      data.numMixes = mixes.size;
      for (var i=0; i < data.songs.length; i++)
      {
        if (mixes.has(i+1)) {
          data.mixes[i] = true;
        }
        else
        {
          data.mixes[i] = false;
        }
      }
      res.render('song-list.ejs', { data });  
    });
});

app.get('/mixer/:id', function (req, res) {

  db.ref("songs/" + `${parseInt(req.params.id) - 1}`)
    .once("value", function(snapshot) {
      var data = {
        "song" : snapshot.val(),
        "userId" : req.session.userId
      }
      console.log(data);
      res.render('mixer.ejs', { data });  
  });
});

app.get('/save/:userId/:songId/:bass/:drums/:other/:vocals/:time', function (req, res) {

  console.log(req.params);
  var date = new Date().toISOString();

  var mix = {
    "userId" : req.params.userId,
    "songId" : req.params.songId,
    "bass" : req.params.bass,
    "drums" : req.params.drums,
    "other" : req.params.other,
    "vocals" : req.params.vocals,
    "time" : req.params.time,
    "datetime" : date
  }

  db.ref("mixes/")
    .push(mix, function() {
      //res.status(204).send(); 
      res.redirect("/song-list")
  });

  db.ref("users/" + req.params.userId + "/mixes/")
    .push(req.params.songId, function() {
  });

});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});