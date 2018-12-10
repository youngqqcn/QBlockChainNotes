'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 12:07
 * @descriptions:
 */

let orderRouter =  require('./router/order');
let express = require("express");
let app = express();


app.use('/order', orderRouter);

app.listen(9999);

