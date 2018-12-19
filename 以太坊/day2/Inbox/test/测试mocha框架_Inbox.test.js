'use strict';

/**
 * @author: yqq
 * @create: 2018-12-18 17:45
 * @descriptions:
 */

const assert = require("assert");


class Dog{
    say(){
        return "wangwang";
    }

    happy(){
        return "hahahah";
    }

}

let dog ;
beforeEach(()=>{
    dog = new Dog();

});


//it函数分组
describe("测试dog", ()=>{

    it('测试dog的say方法', ()=>{
        assert.equal(dog.say(), 'wangwang');
    });

    it('测试dog的hello方法', ()=>{
        assert.equal(dog.happy(), 'hahahah');
    })

});



// //it函数分组
// describe("测试dog", ()=>{
//
//     it('测试dog的say方法', ()=>{
//         const dog = new Dog();
//         assert.equal(dog.say(), 'wangwang');
//     });
//
//     it('测试dog的hello方法', ()=>{
//         const dog = new Dog();
//         assert.equal(dog.happy(), 'hahahah');
//     })
//
// });


// //it函数分组
// describe("测试dog", ()=>{
//
//     it('测试dog的say方法', ()=>{
//         const dog = new Dog();
//         console.log(dog.say());
//     });
//
//     it('测试dog的hello方法', ()=>{
//         const dog = new Dog();
//         console.log(dog.happy());
//     })
//
//
// });