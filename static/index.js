$(document).ready(function() {
          window.roompage = 0;
          window.room = 'general';
          function calc(str){
            var cmd = str.split(' ')[0];
            var a = str.split(' ')[1];
            var b = str.split(' ')[2];
              switch (cmd){
                case '/sum':
                  return +a + +b;
                case '/mul':
                  return a * b;
                case '/dif':
                  return a - b;
                case '/div':
                  return a / b;
                case '/help':
                  var message = 'Available commands:<br>/help<br>/translate [language] [text] - Sends a message to be translated <br>'
                    message +='/sum [a] [b]- Sends a+b<br>/mul [a] [b] - Sends a*b<br>/dif [a] [b] Sends a-b<br>/div [a] [b] Sends a/b'
                  createMessage('', message, '', false)
                  return false
                default:
                  return str;
              }
          }

          function createMessage(authorName, message, time, history){
            var html = '<li class="left clearfix">'
            if (authorName) {
              html += '<div class="name">' + authorName +'</div>'
            }
            html +='<div class="chat-body1 clearfix">'
            html += '<p>' + message + '</p>'
            if (time) {
              html += '<div class="chat_time pull-right">' + time + '</div></div></li>'
            }
            if(history){
              $('#messageChat').prepend(html)
              $('.chat_area').scrollTop(10);
            }else{
              $('#messageChat').append(html)
              $('.chat_area').scrollTop($('.chat_area')[0].scrollHeight);
            }
            $('.name').nameBadge({
                border: {
                          color: '#ddd',
                          width: 3
                        },
                colors: ['#a3a948'],
                text: '#fff',
                size: 50,
                margin: 5,
                middlename: true,
                uppercase: false
              });
          }

          function createLink(authorName, message, url, imageUrl, time){
            var html = '<li class="left clearfix">'
            if (authorName) {
              html += '<div class="name">' + authorName +'</div>'
            }
            html +='<div class="chat-body1 clearfix">'
            html += '<p><a href="' + url+ '" target="blank">'
            if(imageUrl){
              html +='<img src="' + imageUrl + '" width="40" height="40" alt="' +message + '">'
            }
            html += message + '</a></p>'
            if (time) {
              html += '<div class="chat_time pull-right">' + time + '</div></div></li>'
            }
            $('#messageChat').append(html)
            $('.name').nameBadge({
                border: {
                          color: '#ddd',
                          width: 3
                        },
                colors: ['#a3a948'],
                text: '#fff',
                size: 50,
                margin: 5,
                middlename: true,
                uppercase: false
              });
          }

          function createRoomLi(name, create){
            var html = ''
            if(create){
              html = '<li class="left clearfix"><div class="chat-body clearfix"><div class="header_sec"><strong class="primary-font" id="roomName">'
              html += name
              html += '<button type="button" data-name='+ name +' class="pull-right btn btn-success" id="createRoomButton">Create</button></strong></div></div><p>Room with that name isn`t created. You can create room</p></li>'
            }else{
              html = '<li class="left clearfix changeRoom"><div class="chat-body clearfix"><div class="header_sec"><strong class="primary-font" id="roomName">'
              html += name
              html += '</strong></div></div></li>'
            }
            return html
          }

          function createRoomList(rooms, searhValue){
            var html = ''
            if (rooms.length == 0){
              html += createRoomLi(searhValue, true)
            }else{
              for (var i=0; i<rooms.length; i++){
                html += createRoomLi(rooms[i].name, false)
              }
            }
            $('#chatRooms').empty();
            $('#chatRooms').append(html)
            $('#createRoomButton').click(function(e) {
              e.preventDefault();
              $.ajax({
                method: "POST",
                url: "/create_room",
                data: { roomname: $(this).attr('data-name')}
              }).done(function( msg ) {
                  createRoomListMessage(msg['message'])
                  if(msg['success']){
                    room = msg['roomname']
                    window.roompage = 0
                    socket.emit('change_room', {roomname: msg['roomname']});
                  $('#chatRooms').empty();
                  $('#searchRoom').empty()
                }
                });
              });
            $('.changeRoom').click(function(e) {
              e.preventDefault();
              window.room = $(this).find('#roomName').text()
              window.roompage = 0
              socket.emit('change_room', {roomname: window.room});
              getHistoryPage()
            });
          }
          function getHistoryPage(){
                window.roompage++
                $.ajax({
                  method: "GET",
                  url: "/history",
                  data: { 'room': window.room, 'roompage':window.roompage}
                }).done(function( msg ) {
                  console.log(msg)
                    var story = msg
                    for( var i=0; i<story.length; i++){
                      createMessage(story[i].username, story[i].data, story[i].datetime, true)
                    }
                  })
                }
          $('.changeRoomUser').click(function(e) {
              e.preventDefault();
              username = $(this).find('#userName').text()
              window.roompage = 0
              socket.emit('change_room_user', {username: username});
              window.room = $('#chatName').text()
              getHistoryPage()
            });
          $('.chat_area').scroll(function(){
            if ( $('.chat_area').scrollTop() == 0 ){
                  getHistoryPage()
                }
          });

          function createRoomListMessage(msg){
            var html = '<p>' + msg + '</p>'
            $('#chatRooms').empty();
            $('#chatRooms').append(html)
          }

          var namespace = '/chat';
          var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

          socket.on('connect', function() {
                getHistoryPage()
            });

          socket.on('responce_story', function(msg) {
                var story = msg['data']
                for( var i=0; i<story.length; i++){
                    createMessage(story[i].username, story[i].data, story[i].datetime, true)
                  }
            });

          socket.on('response', function(msg) {
                if($('#chatName').text()!==msg.roomname){
                  $('#chatName').text(msg.roomname)
                  $('#messageChat').empty()
                }
                if ($('#chatName').text()== 'general'){
                  $('#leaveRoomButton').hide()
                }else{
                  $('#leaveRoomButton').show()
                }
                if(msg.link){
                  if(msg.link.length>0){
                      createLink(msg.username, msg.title, msg.data, msg.image ,msg.datetime)
                    }else{
                      createMessage(msg.username, msg.data, msg.datetime, false)
                    }
                }
            });


          function sendMessage(e){
              e.preventDefault();
              var msg = calc($('#messageText').val())
                if(msg){
                  socket.emit('message', {data: msg});
                }
                $('#messageText').val('');
          }
          $('#messageForm').submit(function(e) {
              sendMessage(e)
            })
          $('#messageForm').keydown(function(e) {
                var key = e.which;
                  if (key == 13) {
                    sendMessage(e)
                  }
              });
          $('#searchRoom').on('input', function() {
            var searchValue = $(this).val()
            $.ajax({
              method: "POST",
              url: "/find_room",
              data: { roomname: searchValue}
            }).done(function( msg ) {
                createRoomList(msg, searchValue)
              });
          });
          $('#leaveRoomButton').click(function(e) {
            e.preventDefault();
              window.room = 'general'
              window.roompage = 0
              socket.emit('leave');
            });

        });