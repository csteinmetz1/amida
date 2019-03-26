import express from 'express';
import path from 'path';
import firebase from 'firebase-admin';

import bodyParser from 'body-parser';
import cookieParser from 'cookie-parser';
import session from 'express-session';

// Fetch the service account key JSON file contents
var ServiceAccount = require('./keys.json') as firebase.ServiceAccount;

// interfaces
interface User {
  id: string,
  experience: number,
  playback: string,
  mixes: number[]
}

interface Song {
  id: number,
  artist: string,
  title: string,
  tracks: TrackList[]
}

interface TrackList {
  bass: string,
  drums: string,
  other: string,
  vocals: string
}

interface Mix {
  songId: number,
  userId: string,
  bass: number,
  drums: number,
  other: number,
  vocals: number,
  datetime: string,
  time: number
}

interface Session {
  secret: string,
  resave: boolean,
  saveUninitialized: boolean,
  userId: string,
  songs: Song[]
}

interface SongListTemplate {
  userId: string,
  songs: Song[],
  mixes: boolean[],
  nMixes: number
}

interface MixerTemplate {
  userId: string,
  song: Song
}

// setup for firebase real-time database
firebase.initializeApp({
  credential: firebase.credential.cert(ServiceAccount),
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
  .use(session({secret: 'tk421', resave: false, saveUninitialized: true}));

// routes
app.post('/login', function (req, res) { 	
  if (req.session !== undefined) {
    db.ref("users").once("value", function(snapshot) {
      var users:User[] = snapshot.val();
      console.log(req.body.id, Object.keys(users));
      if (Object.keys(users).indexOf(req.body.id) < 0)
      {
        console.log(`User ${req.body.id} not found!`);
        var error = {"text" : `User id (${req.body.id}) not found.`}
        return res.render("login.ejs", error);
      }
      else
      {
        req.session!.userId = req.body.id;
        // get songs from database and save
        db.ref("songs").once("value", function(snapshot) {
          req.session!.songs = snapshot.val();
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
  if (req.session !== undefined) {
    req.session.destroy(function(err) {
      if (err) return console.log(err);
        return res.redirect('/');
    });
  }
});

app.post('/new-user', function (req, res) { 	
  if (req.session !== undefined) {
    req.session.userId = req.body.id;
    var userData = {
      "id" : req.body.id,
      "experience" : req.body.experience,
      "playback" : req.body.playback,
    }
    db.ref("songs").once("value", function(snapshot) {
      req.session!.songs = snapshot.val();
      res.redirect('/song-list');
    });
    db.ref("users/" + req.body.id)
      .set(userData, function() {
    });
  }
});

app.get('/song-list', function (req, res) {

  var data:SongListTemplate = {
    userId: req.session!.userId,
    songs: req.session!.songs,
    mixes: [],
    nMixes: 0
  }

  db.ref("users/" + req.session!.userId + "/mixes/")
    .once("value", function(snapshot) {
      let mixes = new Set();
      if (snapshot.exists())
      {
        mixes = new Set(Object.values(snapshot.val()).map(Number));
      }
      data.nMixes = mixes.size;
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
      var data:MixerTemplate = {
        "song" : snapshot.val(),
        "userId" : req.session!.userId
      }
      console.log(data);
      res.render('mixer.ejs', { data });  
  });
});

app.get('/save/:userId/:songId/:bass/:drums/:other/:vocals/:time', function (req, res) {

  var date = new Date().toISOString();

  var mix:Mix = {
    userId : req.params.userId,
    songId : parseInt(req.params.songId),
    bass : parseFloat(req.params.bass),
    drums : parseFloat(req.params.drums),
    other : parseFloat(req.params.other),
    vocals : parseFloat(req.params.vocals),
    time : parseFloat(req.params.time),
    datetime : date
  }

  db.ref("mixes/")
    .push(mix, function() {
      console.log(mix);
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