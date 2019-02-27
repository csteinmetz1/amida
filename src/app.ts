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
let song: any;

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
  res.render('song-list.ejs', { songs });  
});

app.get('/mixer/:id', function (req, res) {
  db.ref("songs/" + req.params.id)
    .once("value", function(snapshot) {
      song = snapshot.val();
      res.render('mixer.ejs', { song });  
  });
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});