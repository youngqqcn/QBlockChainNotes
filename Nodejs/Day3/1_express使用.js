'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 10:54
 * @descriptions:
 */

let express = require("express");
let app = express();


app.use(express.static('static'));

 app.get('/', (req, res) =>{
     res.send("hello !  this is world!");
});



app.listen(3000);
