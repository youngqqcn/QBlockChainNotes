'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 12:00
 * @descriptions:
 */

let express = require("express");
let app = express();




app.get('/ab+c', (req, res)=>{

    res.send("hello ...........");

});

app.get('/a*z', (req, res)=>{

    res.send("hello ...........");

});


app.listen(3000);
