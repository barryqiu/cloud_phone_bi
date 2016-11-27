/**
 * Created by barryqiu on 2015/10/2.
 */
$('#checkAll').click(function () {
        if (this.checked) {
            $("[name='selectFlag']:checkbox").each(function () { //遍历所有的name为selectFlag的 checkbox
                this.checked = true;
                //console.log($(this));
            })
        } else {   //反之 取消全选
            $("[name='selectFlag']:checkbox").each(function () { //遍历所有的name为selectFlag的 checkbox
                $(this).removeAttr("checked");
                //console.log($(this));
            })
        }
    }
);

function del_all_game(page) {
    event.returnValue = confirm("删除是不可恢复的，你确认要删除吗？");
    var str = "0";
    $("[name='selectFlag']:checkbox").each(function () {
        if (this.checked == true) {
            str += "," + this.id ;
        }
    });
    $.get("/game/del/" + page +"/" + str, function (result) {
        self.location.reload();
    });
}

function del_all_trial_game(page) {
    event.returnValue = confirm("删除是不可恢复的，你确认要删除吗？");
    var str = "0";
    $("[name='selectFlag']:checkbox").each(function () {
        if (this.checked == true) {
            str += "," + this.id ;
        }
    });
    $.get("/trial/game/del/" + page +"/" + str, function (result) {
        self.location.reload();
    });
}

function del_all_game_task(game_id, page) {
    event.returnValue = confirm("删除是不可恢复的，你确认要删除吗？");
    var str = "0";
    $("[name='selectFlag']:checkbox").each(function () {
        if (this.checked == true) {
            str += "," + this.id ;
        }
    });

    $.get("/game/task/"+ game_id + "/" + page +"/del/" + str, function (result) {
        self.location.reload();
    });
}


function del_all_game_server(game_id, page) {
    event.returnValue = confirm("删除是不可恢复的，你确认要删除吗？");
    var str = "0";
    $("[name='selectFlag']:checkbox").each(function () {
        if (this.checked == true) {
            str += "," + this.id ;
        }
    });

    $.get("/game/server/"+ game_id + "/" + page +"/del/" + str, function (result) {
        self.location.reload();
    });
}

function del_all_apk(page) {
    event.returnValue = confirm("删除是不可恢复的，你确认要删除吗？");
    var str = "0";
    $("[name='selectFlag']:checkbox").each(function () {
        if (this.checked == true) {
            str += "," + this.id ;
        }
    });
    $.get("/apk/del/" + page +"/" + str, function (result) {
        self.location.reload();
    });
}

function del_all_apk_category(page) {
    event.returnValue = confirm("删除是不可恢复的，你确认要删除吗？");
    var str = "0";
    $("[name='selectFlag']:checkbox").each(function () {
        if (this.checked == true) {
            str += "," + this.id ;
        }
    });
    $.get("/apk/category/" + page + "/del/" + str, function (result) {
        self.location.reload();
    });
}

function del_all_apk_category_apk(category_id, page) {
    event.returnValue = confirm("删除是不可恢复的，你确认要删除吗？");
    var str = "0";
    $("[name='selectFlag']:checkbox").each(function () {
        if (this.checked == true) {
            str += "," + this.id ;
        }
    });
    $.get("/apk/category/"+ category_id +"/apk/"+ page +"/del/"+ str, function (result) {
        self.location.reload();
    });
}



function delete_confirm()
{
    event.returnValue = confirm("删除是不可恢复的，你确认要删除吗？");
}