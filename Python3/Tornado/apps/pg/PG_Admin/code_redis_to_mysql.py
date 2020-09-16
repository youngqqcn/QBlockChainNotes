import re
import redis
import pymysql
from PG_Admin.settings import REDIS_HOST, REDIS_PORT, REDIS_API_KEY_DB_NAME_CACHE, ENV_NAME
from config.config import config


rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_API_KEY_DB_NAME_CACHE, decode_responses=True)

db = pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USERNAME, password=config.MYSQL_PWD,
                     port=config.MYSQL_PORT, database=f'pg_database_{ENV_NAME.lower()}',
                     autocommit=True, read_timeout=10, write_timeout=10)

cursor = db.cursor()

##处理redis已有googlecode 带来第一次上生产问题

def code_redis_to_mysql():

    try:

        res = rds.keys()

        for i in res:
            if f'{ENV_NAME}_code_admin' in i:
                secret = rds.get(i)


                pattern = re.compile(f'{ENV_NAME}_code_admin_(\d+)')
                pro_id = pattern.findall(i)[0]

                sql = """insert into tb_google_code (pro_id, `key`, is_superuser) 
                                        value('%s', '%s', %d) """ % (pro_id, secret, 1)
                cursor.execute(sql)

            elif f'{ENV_NAME}_code' in i:
                secret = rds.get(i)

                pattern = re.compile(f'{ENV_NAME}_code_(\d+)')
                pro_id = pattern.findall(i)[0]

                url = f'{ENV_NAME}_first_login_' + pro_id
                is_exist = rds.get(url)
                if is_exist:
                    logined = 1
                else:
                    logined = 0

                sql = """insert into tb_google_code (pro_id, `key`, logined) 
                                                    value('%s', '%s', %d) """ % (pro_id, secret, logined)
                cursor.execute(sql)

                pass

        db.commit()
    except Exception as e:
        print(f'code_redis_to_mysql error : {e}')
        pass

def main():
    code_redis_to_mysql()


if __name__ == '__main__':
    main()