

//文件服务器


let http = require("http");
let fs = require("fs");
let path = require("path");



let server = http.createServer((req, res)=>{

    if(req.url === '/favicon.ico'){
        res.end("");
        return;
    }

    res.writeHead(200, {'content-type' : 'text/html; charset=utf-8'});
    showDir(req, res);

});

server.listen(5000);

function showDir(req, res) {


    let target = 'test';
    if(req.url !== '/'){
        target = req.url;
        target = target.substr(1);
    }
    console.log(target);

    fs.readdir(target, (err, files)=>{
        let str = "";
        files.forEach(f =>{
            let fpath = path.join(target, f);
            console.log(fpath);
            let stat = fs.statSync(fpath);
            if(stat.isDirectory()){
                   str += `<li><a href="${fpath}">${f}</a></li>` ;
            }else{
                str += `<li>${f}</li>`;
            }
        });
        res.end(makeHtml(str));
    });

}


function makeHtml(str) {

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>

<div>
    <ul>
    ${str}
    </ul>
</div>

</body>
</html>`;


}






