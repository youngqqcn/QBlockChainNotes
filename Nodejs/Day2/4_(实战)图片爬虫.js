'use strict';

let http = require("http");
let iconv = require("iconv-lite");  //用来解码gbk
let fs = require("fs");
let cheerio = require("cheerio");
let path = require('path');





http.get("http://www.27270.com/ent/meinvtupian/", res=>{
    
    let htmlBuf = [];
    res.on('data', chunk=>{
        htmlBuf.push(chunk);
    });


    res.on('end', ()=>{
        let htmlStr = iconv.decode(Buffer.concat(htmlBuf), "gbk");
        // console.log(htmlStr);

        let imgs = [];
        imgs = ExtraDataFromHtml(htmlStr);

        DownloadImg(imgs);
    });
});






function ExtraDataFromHtml(html) {

    let $ = cheerio.load(html);
    let imgArr = $('div.MeinvTuPianBox>ul>li>a>i>img').toArray();

    let retArr = [];
    imgArr.forEach(imgObj=>{
        console.log($(imgObj).attr("src"), "\t", $(imgObj).attr("alt"));

        retArr.push({
            src:$(imgObj).attr("src"),
            title:$(imgObj).attr("alt")
        });

    });
    return retArr;
}


function DownloadImg(imgs) {

    imgs.forEach(imgObj=>{


        http.get(imgObj.src, res=>{

            let imgPath = path.join('imgs', imgObj.title + path.extname(imgObj.src));
            let writer = fs.createWriteStream(imgPath);

            res.pipe(writer);


        });


        // console.log(imgObj.src, "\t", imgObj.title);

    });

}