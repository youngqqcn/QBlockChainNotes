


//数组
arr = [1, 2, 3, 4];
let[a, b, c, d] = arr;
console.log(a, b, c, d);



//对象
const obj = {name:"yqq", addr:"shenzhen", age:10};
let{name, addr, age} = obj;
console.log(name, addr, age);


//函数参数
const person = {name:"yqq", age:11};
function showInfo({name, age}) {
    console.log(name, age)
}
showInfo(person);





