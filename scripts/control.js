 function showGallery(){
  $(".bottom-container").show();
};

 var socket = io();
   socket.on('liveStream', function(url) {
     $('#stream').attr('src', url);
     $('.start').hide();
   });

   socket.on('img',function(msg){
    str = JSON.stringify(msg.src);

    $('#latest-thumb').attr("src", "captured/thumb_"+str+".jpg");
    $('#selected-image').attr("src", "captured/full_"+str+".jpg");
  });

   socket.on('imginit',function(msg){
    console.log("got imginit");
    var array = msg.src;
    for(var i = 0; i < array.length; i++){
       $("#all-images").append("<div class='pure-u-1-8'> <img src='captured/thumb_"+array[i]+"'/></div>");
    }
   

  });
 
   function startStream() {
     socket.emit('start-stream');
     $('.start').hide();
   }
  

   function upMove(){
	   console.log("emit move up");
 	    socket.emit('command',{'type':'move', 'var':'dec', 'val':'up'});
   }
  
   function downMove(){
 	  socket.emit('command',{'type':'move', 'var':'dec', 'val':'down'});
   }
  
   function leftMove(){
 	  socket.emit('command',{'type':'move', 'var':'alt', 'val':'left'});
   }
  
   function rightMove(){
 	  socket.emit('command',{'type':'move', 'var':'alt', 'val':'right'});
   }
  
   function capture(){
 	  socket.emit('command',{'type':'capture'});
   }


var scopeSettings = {'type':'settings','exposure':'1', 'wb':'off', 'ISO':'100', 'dec_num_steps':'1', 'alt_num_steps':'1', 'focus_num_steps':'1', 'dec_step_type':'micro', 'alt_step_type':'micro', 'focus_step_type':'micro', 'wb_gains':'1' }

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
      value = $('.range-slider__value'),
      dropdown = $('.settingdrop');
      setting = $('.setting');

 
    
  slider.each(function(){

    value.each(function(){
      var value = $(this).prev().attr('value');
      $(this).html(value);
    });

    range.on('input', function(){
      $(this).next(value).html(this.value);
     
      
    
    });
  });

  $('#exposure').on('input', function(){
    scopeSettings[$(this).attr('id')] = $(this).val();
    socket.emit('command',scopeSettings);
  });

  $('#ISO').on('input', function(){
    scopeSettings[$(this).attr('id')] = $(this).val();
    socket.emit('command',scopeSettings);
  });

  $('#wb').on('input', function(){
    scopeSettings[$(this).attr('id')] = $(this).val();
    socket.emit('command',scopeSettings);
  });

  $('#wb_slider').on('input', function(){
    
      scopeSettings['wb_gains'] = $(this).val();
      socket.emit('command',scopeSettings);
    
    
    
  });

  $('#focus_step_type').on('input', function(){
    scopeSettings[$(this).attr('id')] = $(this).val();
    socket.emit('command',scopeSettings);
  });

  $('#focus_num_steps').on('input', function(){
    scopeSettings[$(this).attr('id')] = $(this).val();
    socket.emit('command',scopeSettings);
  });

  $('#alt_step_type').on('input', function(){
    scopeSettings[$(this).attr('id')] = $(this).val();
    socket.emit('command',scopeSettings);
  });

  $('#alt_num_steps').on('input', function(){
    scopeSettings[$(this).attr('id')] = $(this).val();
    socket.emit('command',scopeSettings);
  });

  $('#dec_step_type').on('input', function(){
    scopeSettings[$(this).attr('id')] = $(this).val();
    socket.emit('command',scopeSettings);
  });

  $('#dec_num_steps').on('input', function(){
    scopeSettings[$(this).attr('id')] = $(this).val();
    socket.emit('command',scopeSettings);
  });




};

rangeSlider();














  
  
});
