'use strict';

/**
 * @author: yqq
 * @create: 2018-12-09 14:17
 */

let crypto = require("crypto");

let sha256 = crypto.createHash("sha256");

sha256.update("helloworld");

console.log(sha256.digest('hex'));




//AES算法加密
let data = "helloworld";
let password = "123";
const cipher = crypto.createCipher('aes192', password);
let encrypted = cipher.update(data, 'utf-8', 'hex' );
encrypted += cipher.final('hex');
console.log(encrypted);


//AES算法解密
const  decipher = crypto.createDecipher('aes192', password);
let encrydata = encrypted;
let decrypted = decipher.update(encrydata, 'hex', 'utf-8');
decrypted += decipher.final('utf-8');
console.log(decrypted);
 
