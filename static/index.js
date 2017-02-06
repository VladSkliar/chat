$(document).ready(function() {
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
                  createMessage('', message, '')
                  return false
                default:
                  return str;
              }
          }


          function createMessage(authorName, message, time){
            var html = '<li class="left clearfix">'
            if (authorName) {
              html += '<div class="name">' + authorName +'</div>'
            }
            html +='<div class="chat-body1 clearfix">'
            html += '<p>' + message + '</p>'
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
            console.log(rooms, searhValue)
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
              console.log($(this).attr('data-name'));
              $.ajax({
                method: "POST",
                url: "/create_room",
                data: { roomname: $(this).attr('data-name')}
              }).done(function( msg ) {
                console.log(msg)
                  createRoomListMessage(msg['message'])
                });
              });
            $('.changeRoom').click(function(e) {
              e.preventDefault();
              socket.emit('change_room', {roomname: $(this).find('#roomName').text()});
            });
          }

          function createRoomListMessage(msg){
            var html = '<p>' + msg + '</p>'
            $('#chatRooms').empty();
            $('#chatRooms').append(html)
          }

          var namespace = '/test';
          var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

          socket.on('connect', function() {
                // socket.emit('message', {data: 'I\'m connected!'});
            });

          socket.on('response', function(msg) {
                console.log(msg)
                if($('#chatName').text()!==msg.roomname){
                  $('#chatName').text(msg.roomname)
                  $('#messageChat').empty()
                }
                if ($('#chatName').text()== 'general'){
                  $('#leaveRoomButton').hide()
                }else{
                  $('#leaveRoomButton').show()
                }
                createMessage(msg.username, msg.data, msg.datetime)
                $('.chat_area').scrollTop($('.chat_area')[0].scrollHeight);
            });

          $('#sendMessage').click(function(e) {
            e.preventDefault();
              var msg = calc($('#messageText').val())
              if(msg){
                socket.emit('message', {data: msg});
              }
              $('#messageText').val('');
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
              socket.emit('leave');
            });

        });