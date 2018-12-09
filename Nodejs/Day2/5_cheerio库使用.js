'use strict';

/**
 * @author: yqq
 * @create: 2018-12-09 15:00
 * @descriptions:
 */

let cheerio = require("cheerio");


let html = `
<div>
    <h2>哈哈哈</h2>
    <h2>嘻嘻嘻嘻</h2>
    <a href="http://www.baidu.com"> 点击跳到百度</a>
    <a href="http://www.sina.com"> 点击跳到新浪</a>
    <a href="http://www.google.com"> 点击跳到谷歌</a>
</div>
`;


let $ = cheerio.load(html);

console.log(  $('div').children().first().text() );
console.log( $('h2').text() );

console.log($('div>a').text());
console.log($('div>a').attr('href'));



//获取多个
let arr = $('div>a').toArray();
arr.forEach(obj=>{
    console.log($(obj).text());
    console.log($(obj).attr("href"));
});











