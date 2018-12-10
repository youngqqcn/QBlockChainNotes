'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 11:23
 * @descriptions:
 */


/*
使用  Postman 测试
 */



let express = require("express");
let app = express();

// app.use('/static', express.static('static'));

app.get('/', (req, res)=>{
    res.send('hello ' + req.method)
});

app.post('/', (req, res)=>{
    res.send('hello ' + req.method)
});

app.put('/', (req, res)=>{
    res.send('hello ' + req.method)
});

app.delete('/', (req, res)=>{
    res.send('hello ' + req.method)
});

app.listen(3000);