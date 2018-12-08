let fs = require("fs");
let http = require("http");



let server =  http.createServer((req, res)=>{
    console.log(req.url);

    //res.writeHead(200, {'Content-Type':'application/json;charset=utf-8'}); //解决乱码问题
    res.writeHead(200, {'Content-Type':'text/html;charset=utf-8'}); //解决乱码问题

    let person = {
        name: "羊轻轻",
        age : 55
    };


    //res.end(JSON.stringify(person));

    if(req.url === "/"){
        let html = fs.readFileSync("13_http.html");
        res.end(html);
    }else if(req.url === "/a"){
        let html = fs.readFileSync("13_http_a.html");
        res.end(html);
    }
});
server.listen(9999);