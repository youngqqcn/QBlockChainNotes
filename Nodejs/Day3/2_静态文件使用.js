'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 11:18
 * @descriptions:
 */

let express = require("express");
let app = express();


app.use(express.static('static'));



app.listen(3000);