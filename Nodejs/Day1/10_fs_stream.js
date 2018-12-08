
let fs = require("fs");


//只能读取 2G(0x7fffffff) 以下
//fs.readFile("")

let reader = fs.createReadStream("G:\\视频\\blockchain1\\06_nodejs课程\\day01\\video\\12.fs模块.mp4");
let writer = fs.createWriteStream("copy.mp4");
let len = 0;
reader.on('data', (chunk)=>{
    console.log(chunk.length);
    len += chunk.length;
    writer.write(chunk, ()=>{
        console.log("写入了一块")
    });
});


reader.on('end', ()=>{
    console.log("读完了"+ len)
});

writer.on('end', ()=>{
    console.log("写完了")
});
