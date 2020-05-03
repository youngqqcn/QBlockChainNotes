

//使用 jQuery
$(document).ready(function () {

    document.getElementById("btn_test_ajax").onclick = function () {
        $.ajax({
            type: "get",
            url : "/test_ajax/",
            dataType : "json",
            success : function (data, status) {
                console.log(data);
                node = document.getElementById("stu_list");

                //倒叙删除所有子节点
                console.log("node'length : %d" , node.length);
                for(var idx = node.length - 1;  idx > 0; idx --){
                    node.removeChild( node[idx] );
                    console.log("remove %d", idx);

                }


                //创建一个新的节点
                newnode = document.createElement("ul");
                newnode.setAttribute("id", "stu_list");

                stus  =  data['data'];
                for(var i = 0; i < stus.length; i++){

                    var newitem = document.createElement("li");
                    var strtmp =  stus[i]['sname'] + "---" +  stus[i]['sconted']  ;

                    newitem.appendChild( document.createTextNode(strtmp) );
                    newnode.appendChild( newitem );
                }

                //使用新的节点替换旧的节点, 防止一直在后面追加!
                node.replaceWith(  newnode );

            }
        })
    }

});

//
// function testajax(){
//     console.log("dddddddddddddddddddddd");
//     document.getElementById("btn_test_ajax").onclick = function () {
//         $.ajax({
//             type: "get",
//             url: "/test_ajax/",
//             dataType: "json",
//             success: function (data, status) {
//                 console.log(data)
//             }
//         })
//     }
// }


