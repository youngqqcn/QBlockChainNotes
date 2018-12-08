
//函数参数默认值
function show(name, addr="shenzhen") {
    console.log(name, addr)
}

show("yqq");
show("Tom");
show("Tom", "Beijing");


//lambda函数


var function1 = (age) => {
    console.info(age);
};
function1(13);
