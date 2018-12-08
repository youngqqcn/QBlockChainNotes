
let fs = require("fs");



reader =  fs.createReadStream("copy.mp4" );
writer = fs.createWriteStream("copy_copy.mp4");

reader.pipe(writer);  //管道使用


writer.on('end', ()=>{

    console.log("写完了")
});