var express = require('express');
var fs = require('fs');
var app = express();

app.get('/stream', function(req, res) {
    console.log("/stream  connected");

    res.writeHead(200, {
        "Content-Type":"text/event-stream",
        "Cache-Control":"no-cache",
        "Connection":"keep-alive"
    });

    res.write("retry: 10000\n");
    res.write("event: connecttime\n");
    res.write("data: " + (new Date()) + "\n\n");
    res.write("data: " + (new Date()) + "\n\n");

    interval = setInterval(function() {
        console.log("responsed");
        res.write("data: " + (new Date()) + "\n\n");
    }, 1000);

    req.connection.addListener("close", function () {
        console.log("client closed");
        clearInterval(interval);
    }, false);
});

app.use(function(req, res) {
    fs.readFile('./index.html', 'utf8',function(err, html) {
        if (err) {
            console.log(err);
            return
        }
        res.send(html)
    })
});

app.listen(9999, function(err) {
    if (err) {
        console.log(err);
        return
    }
    console.log('listening on port 9999')
});