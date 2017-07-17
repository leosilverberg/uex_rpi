 // var socket = io();
 //   socket.on('liveStream', function(url) {
 //     $('#stream').attr('src', url);
 //     $('.start').hide();
 //   });
 
 //   function startStream() {
 //     socket.emit('start-stream');
 //     $('.start').hide();
 //   }
  
 //   function testMove(){
 // 	socket.emit('test-move');
 //   }
  
 //   function upMove(){
 // 	  socket.emit('up-move');
 //   }
  
 //   function downMove(){
 // 	  socket.emit('down-move');
 //   }
  
 //   function leftMove(){
 // 	  socket.emit('left-move');
 //   }
  
 //   function rightMove(){
 // 	  socket.emit('right-move');
 //   }
  
 //   function capture(){
 // 	  socket.emit('capture');
 //   }

$(document).ready(function() {

  
  var canvas = document.getElementById('videoCanvas');
  var ctx = canvas.getContext('2d');
  
  ctx.fillText('Loading...', canvas.width/2-30, canvas.height/3);
  // ctx.scale(-1,1);


  // Setup the WebSocket connection and start the player
   var client = new WebSocket('ws://172.24.1.1:8084/');
   var player = new jsmpeg(client, {canvas:canvas});
   console.log("added stream")

  updateFinderSize();


  $(window).resize(function() {
    updateFinderSize();
  });

  function updateFinderSize() {
    console.log("updating findersize");
    canvas.width = $("#finderDiv").width();
    // canvas.height = $("#finderDiv").height();
    canvas.style.width = $("#finderDiv").width();
    $("canvas").css("width", $("#finderDiv").width()+"px");
 
    ctx.fillStyle = 'black';
    ctx.fillRect(0,0,canvas.width, canvas.height)
    console.log($("#finderDiv").width())
  }


var rangeSlider = function(){
  var slider = $('.range-slider'),
      range = $('.range-slider__range'),
      value = $('.range-slider__value');
    
  slider.each(function(){

    value.each(function(){
      var value = $(this).prev().attr('value');
      $(this).html(value);
    });

    range.on('input', function(){
      $(this).next(value).html(this.value);
    });
  });
};

rangeSlider();












  
  
});
