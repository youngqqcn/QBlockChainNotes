
let fs = require("fs");
let path = require("path");
let http = require("http");



http.get("http://www.baidu.com", (res)=>{

    // console.log(res.toString())

    let data = '';
    res.on('data', (chunk)=>{
        data += chunk.toString();
    });

    res.on('end', ()=>{
        console.log(data);
    });

});








