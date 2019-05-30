import express from 'express';
import path from 'path';
import firebase from 'firebase-admin';

import bodyParser from 'body-parser';
import cookieParser from 'cookie-parser';
import session from 'express-session';

// Fetch the service account key JSON file contents
var ServiceAccount = require(__dirname + '/keys.json') as firebase.ServiceAccount;

// interfaces
interface User {
  id: string,
  experience: number,
  playback: string,
  mixes: number[],
  skips: number[],
  nMixes: number,
  nSkips: number
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
  song: Song,
  nMixes: number,
  nSkips: number
}

/**
 * Randomly shuffle an array
 * https://stackoverflow.com/a/2450976/1293256
 * @param  {Array} array The array to shuffle
 * @return {String}      The first item in the shuffled array
 */
var shuffle = function (array:number[]) {

	var currentIndex = array.length;
	var temporaryValue, randomIndex;

	// While there remain elements to shuffle...
	while (0 !== currentIndex) {
		// Pick a remaining element...
		randomIndex = Math.floor(Math.random() * currentIndex);
		currentIndex -= 1;

		// And swap it with the current element.
		temporaryValue = array[currentIndex];
		array[currentIndex] = array[randomIndex];
		array[randomIndex] = temporaryValue;
	}

	return array;

};

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
/*
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

*/

app.post('/new-user', function (req, res) { 	
  if (req.session !== undefined) {
    var userData = {
      "experience" : req.body.experience,
      "playback" : req.body.playback,
    }
    db.ref("songs").once("value", function(snapshot) {
      req.session!.songs = snapshot.val();
      req.session!.mix_order = shuffle(Array.from({length: 100}, (x,i) => i+1));
      db.ref("users/" + req.session!.userId + "/nSkips/").set(0, function() {});
      db.ref("users/" + req.session!.userId + "/nMixes/").set(0, function() {});
      res.redirect('/mixer/'+ req.session!.mix_order.pop());
    });
    var new_post_ref = db.ref("users/")
      .push(userData, function() {
    });
    req.session.userId = new_post_ref.key;
  }
});

app.get('/next/:id/:type', function (req, res) { 	
  if (req.session !== undefined) {
    var nSkips:number;
    if (req.params.type == "skip") {
       db.ref("users/" + req.session.userId + "/nSkips/")
        .once("value", function(snapshot) {
          nSkips = snapshot.val() + 1;
          db.ref("users/" + req.session!.userId + "/nSkips/")
            .set(nSkips, function() {
          });
          db.ref("users/" + req.session!.userId + "/skips/")
            .push(req.params.id, function() {
          });
        })
    }
    else {
      var nMixes:number;
      db.ref("users/" + req.session.userId + "/nMixes/")
        .once("value", function(snapshot) {
          nMixes = snapshot.val() + 1;
          db.ref("users/" + req.session!.userId + "/nMixes/")
            .set(nMixes, function() {});
          db.ref("users/" + req.session!.userId + "/mixes/")
            .push(req.params.id, function() {});
        })
    }
    res.redirect('/mixer/'+ req.session!.mix_order.pop());
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

  var nMixes:number;
  var nSkips:number;
  var song:Song;

  db.ref("songs/" + `${parseInt(req.params.id) - 1}`)
    .once("value", function(snapshot) {
      song = snapshot.val();
      db.ref("users/" + req.session!.userId + "/nMixes")
        .once("value", function(snapshot) {
          nMixes = snapshot.val();
          db.ref("users/" + req.session!.userId + "/nSkips")
          .once("value", function(snapshot) {
            nSkips = snapshot.val();
            var data:MixerTemplate = {
              "song" : song,
              "userId" : req.session!.userId,
              "nMixes" : nMixes,
              "nSkips" : nSkips
            }
            console.log(data);
            res.render('mixer.ejs', { data });  
          })
        })
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
      res.redirect(`/next/${req.params.songId}/save`)
  });
});

app.listen(80, function () {
  console.log('amida listening on port 80!');
});