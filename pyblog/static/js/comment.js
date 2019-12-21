$(document).ready(function(){
        $("#comment-form").submit(function(e){
            e.preventDefault();
            var form= {
                email:'input[name="email"]',
                content:'textarea[name="content"]',
                parent_id:'input[name="parent_id"]',
                at_id:'input[name="at_id"]',
            };
            data = {
                email:$(form.email).val(),
                content:$(form.content).val(),
                source_id:"1",
                parent_id:$(form.parent_id).val(),
                at_id:$(form.at_id).val(),
            };
            var article_uuid = $('#article-uuid').text()
            $.ajax({
                type: "POST",
                url: `/comment/${article_uuid}/`,
                data: $("#comment-form").serialize(),
                success: function(data, status,jqXHR){
                    console.log(data,status)
                    if (data.code == 0){ //评论成功
                    var comment = `<div class="media text-muted pt-3">
                      <img src="${data.data.avatar}" class="mr-3" alt="...">
                      <div class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                        <div class="d-flex justify-content-between align-items-center w-100">
                            <span class="d-block">${data.data.nick}</span>
                            <small class="d-block text-right mt-3">
                                <span>刚刚</span>
                                <a class="comment-reply " href="#">回复</a>
                            </small>
                        </div>
                        <strong class="text-gray-dark">${data.data.content}</strong>
                      </div>
                    </div>`
                    $("#comment").prepend(comment);
                    $("#comment-form")[0].reset(); //清空表单
                    } else {
                        console.log(data.msg)
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
        $(window).scroll(function(){
            if($(window).scrollTop() == $(document).height() - $(window).height()) {
                if (has_next_page) {
                    $.ajax({
                    type: 'get',
                    url: `/comment/${article_uuid}/?page=${next_page}&size=${page_size}`,
                    success: function(data, status) {
                        if (data.code == 0) {
                            has_next_page = data.data.has_next;
                            next_page = data.data.has_next?next_page+1:next_page+0;
                            var list = data.data.list;
                            var comments = ''
                            list.map(function(d){
                                var comment = `<div class="media text-muted pt-3">
                                              <img src="${d.avatar}" alt="..." class="mr-3">
                                              <div class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                                                <div class="d-flex justify-content-between align-items-center w-100">
                                                    <span class="d-block">${d.nick}</span>
                                                    <small class="d-block text-right mt-3">
                                                        <span>${d.create_date}</span>
                                                        <a class="comment-reply " href="#">回复</a>
                                                    </small>
                                                </div>
                                                <strong class="text-gray-dark">${d.content}</strong>
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
});