var socket = io();
  socket.on('liveStream', function(url) {
    $('#stream').attr('src', url);
    $('.start').hide();
  });
 
  function startStream() {
    socket.emit('start-stream');
    $('.start').hide();
  }
  
  function testMove(){
	socket.emit('test-move');
  }
  
  function upMove(){
	  socket.emit('up-move');
  }
  
  function downMove(){
	  socket.emit('down-move');
  }
  
  function leftMove(){
	  socket.emit('left-move');
  }
  
  function rightMove(){
	  socket.emit('right-move');
  }
  
  
