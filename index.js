'use strict';

var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var fs = require('fs');
var path = require('path');

var spawn = require('child_process').spawn;
var proc;

var sockets = {};

var ON_DEATH = require('death');

var PythonShell = require('python-shell');
var pShell = new PythonShell('camera_stream.py', {mode:'json',scriptPath:"/home/pi/uex_rpi/scripts/", pythonOptions: ['-u'], pythonPath:"python3"});
console.log("Started camera_stream.py");

app.use('/', express.static(path.join(__dirname, 'stream')));
app.use('/scripts', express.static(path.join(__dirname, 'scripts')));



app.get('/', function(req, res) {
  res.sendFile(__dirname + '/index.html');
});

http.listen(3000, function() {
  console.log('listening on *:3000');
});

io.on('connection', function(socket) {
 
  sockets[socket.id] = socket;
  console.log("Total clients connected : ", Object.keys(sockets).length);
 
  socket.on('disconnect', function() {
    delete sockets[socket.id];
  });
 
  socket.on('start-stream', function() {
    startStreaming(io);
  });
  
  socket.on('test-move', function(){
	testMove();
  });
  
  socket.on('up-move', function(){
	console.log("up node");
	step('up');
  });
  
  socket.on('down-move', function(){
	step('down');

  });
  
  socket.on('left-move', function(){
	step('left');
  });
  
  socket.on('right-move', function(){
	step('right');
  });
  
  socket.on('capture', function(){
	 step('capture'); 
  });
  
  socket.on("command", function(data) {
	console.log("[js] got message: " +data);
    // pShell.send(data);
  });
  
 
});

pShell.on('message', function (message){
	if(message > ""){
		console.log("[js] got message: " +message);
	}
	
});

function step(dir){
	console.log("sending command");
	// pShell.send(dir);
}

ON_DEATH(function(signal,err){
	pShell.end(function(){
		console.log("ending python");
	});
});
