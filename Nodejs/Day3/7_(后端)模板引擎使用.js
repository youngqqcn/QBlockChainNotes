'use strict';

let express = require("express");
let app = express();




app.set('views', 'template');
app.set('view engine', 'jade'); //设置模板引擎




app.get('/', (req, res)=>{

    res.render('index', {
        pageTitle : "我是标题",
        message : "我是消息"
    });

});


app.listen(8888);