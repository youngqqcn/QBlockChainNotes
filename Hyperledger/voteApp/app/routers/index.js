const router = require('koa-router')()
const IndexController = require('./../controllers/index')

router.get('/',IndexController.indexPage)
    .get('/saveUser', IndexController.saveUser)

module.exports = router