$(document).ready(function(){
        $("#comment-form").submit(function(e){
            e.preventDefault();
            var article_uuid = $('#article-uuid').text()
            $.ajax({
                type: "POST",
                url: `/comment/${article_uuid}/`,
                data: $("#comment-form").serialize(),
                success: function(data, status,jqXHR){
                    if (data.code == 0){ //评论成功
                    var comment = `<div class="media text-muted pt-3 " id="${data.data.id}">
                      <img src="${data.data.avatar}" class="mr-3" alt="...">
                      <div class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                        <div>
                          <span class="text-primary">${data.data.nick}:</span>
                          <strong class="text-gray-dark">${data.data.content}</strong>
                        </div>
                        <div class="rp">
                            <div class="time s-fc4">刚刚</div>
                            <a class="comment-reply " href="javascript:;" data-to="${data.data.id}">回复</a>
                        </div>
                      </div>
                    </div>`
                    $("#comment").prepend(comment);
                    $("#comment-form")[0].reset(); //清空表单
                    } else {
//                        console.log(data.msg);
                    }
                },
                dataType: "json",
                error: function(jqXHR,text){
                },
            });
        });

        var has_next_page = true;
        var next_page = 2;
        var page_size = 10;
        var article_uuid = $('#article-uuid').text()
        var comment_count = $('#comment_count').text()
        $(window).scroll(function(){
            if($(window).scrollTop() == $(document).height() - $(window).height()) {
                if (has_next_page) {
                    $.ajax({
                    type: 'get',
                    url: `/comment/${article_uuid}/?page=${next_page}&size=${page_size}&count=${comment_count}`,
                    success: function(data, status) {
                        if (data.code == 0) {
                            has_next_page = data.data.has_next;
                            next_page = data.data.has_next?next_page+1:next_page+0;
                            var list = data.data.list;
                            var comments = ''
                            list.map(function(d){
                                var replies = "";
                                d.reply.map(function(r){
                                    var reply = `<div class="media text-muted pt-3" id="${r.id}">
                                      <img src="${r.avatar}" alt="..." class="mr-3">
                                      <div class="media-body pb-3 mb-0 lh-125 border-bottom border-gray">
                                          <div>
                                                  <span class="text-primary">${r.nick}</span>
                                                  <span>回复</span> <span class="text-primary">${r.at__nick}</span>:
                                                  <strong class="text-gray-dark">${r.content}</strong>
                                          </div>
                                          <div class="rp">
                                              <div class="time s-fc4">${r.create_date}</div>
                                              <a class="comment-reply" href="javascript:;"  data-to="${r.id}">回复</a>
                                          </div>
                                      </div>
                                    </div>`
                                    replies += reply;
                                });
                                var comment = `<div class="media text-muted pt-3" id="${d.id}">
                                              <img src="${d.avatar}" alt="..." class="mr-3">
                                              <div class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                                              <div>
                                                  <span class="text-primary">${d.nick}: </span>
                                                  <strong class="text-gray-dark">${d.content}</strong>
                                              </div>
                                              <div class="rp">
                                                <div class="time s-fc4">${d.create_date}</div>
                                                <a class="comment-reply" href="javascript:;" data-to="${d.id}">回复</a>
                                              </div>
                                              ${replies}
                                              </div>
                                            </div>`
                                comments += comment
                            });
                            $("#comment").append(comments);
                        }
                    }
                    });
                }

            }
        });

        $("body").on('click', '.comment-reply', function(){
            var parent_id = "";
            var at_id = $(this).data('to');
            if($(this).parent().parent().parent().parent().attr("id") == "comment"){
                parent_id = at_id;
            } else {
                parent_id = $(this).parent().parent().parent().parent().parent().attr("id");
            }
            var reply = $("#comment-reply-form");
            $("#comment-reply-form input[name=parent_id]").val(parent_id);
            $("#comment-reply-form input[name=at_id]").val(at_id);
            $(this).parent().append(reply);
            if (reply.hasClass("d-none")){
                reply.removeClass("d-none");
            } else {
                reply.addClass('d-none');
            };
            reply[0].reset();
        });

        $("#comment-reply-form").submit(function(e){
            e.preventDefault();
            var article_uuid = $('#article-uuid').text()
            $.ajax({
                type: "POST",
                url: `/comment/${article_uuid}/`,
                data: $("#comment-reply-form").serialize(),
                success: function(data, status,jqXHR){
                    if (data.code == 0){ //评论成功
                    var comment = `<div class="media text-muted pt-3" id="${data.data.id}">
                      <img src="${data.data.avatar}" class="mr-3" alt="...">
                      <div class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                        <div>
                          <span class="text-primary">${data.data.nick}: </span>
                          <strong class="text-gray-dark">${data.data.content}</strong>
                        </div>
                        <div class="rp">
                            <div class="time s-fc4">刚刚</div>
                            <a class="comment-reply" href="javascript:;" data-to="${data.data.id}">回复</a>
                        </div>
                      </div>
                    </div>`
                    $("#" + data.data.parent_id).children().append(comment);
                    $("#comment-reply-form")[0].reset(); //清空表单
                    $("#comment-reply-form").addClass('d-none');
                    } else {
                        console.log(data.msg);
                    }
                },
                dataType: "json",
                error: function(jqXHR,text){
                },
            });
        });

});