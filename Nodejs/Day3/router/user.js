'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 12:37
 * @descriptions:
 */

let express = require("express");
let router = express.Router();



router.use((req, res, next)=>{

    console.log("路由级别中间件");
    next();

});

router.post('/register', (req, res)=>{

    res.send("user register");

});

router.get('/list', (req, res)=>{
    res.send("user list");
});


module.exports=router;