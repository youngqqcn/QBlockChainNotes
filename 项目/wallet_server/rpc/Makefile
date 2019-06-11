deps:
	@sudo yum -y install python-devel
	@sudo yum -y install epel-release
	@sudo yum -y install python-pip
	@pip install --upgrade pip
	@sudo yum install -y setuptool
	@sudo yum -y install gcc gcc-c++ kernel-devel
	@sudo yum -y install openssl-devel
	@pip install -r requirements.txt


retart: stop start


#for dev
start-testnet:clean
	@rm -rf constant.py
	@cp -f ./config/testnet  constants.py
	@nohup /usr/bin/python  server.py &  > /dev/null

start-mainnet:clean
	@rm -rf constant.py
	@cp -f ./config/mainnet  constants.py
	@nohup /usr/bin/python  server.py &  > /dev/null


#for others
start-dev:clean
	@rm -rf constant.py
	@cp -f ./config/testnet  constants.py
	@nohup /usr/bin/python  server.py &  > /dev/null

start-sit:clean
	@rm -rf constant.py
	@cp -f ./config/testnet  constants.py
	@nohup /usr/bin/python  server.py &  > /dev/null

start-uat:clean
	@rm -rf constant.py
	@cp -f ./config/testnet  constants.py
	@nohup /usr/bin/python  server.py &  > /dev/null

start-pro:clean
	@rm -rf constant.py
	@cp -f ./config/mainnet  constants.py
	@nohup /usr/bin/python  server.py &  > /dev/null


stop: 
	@kill -9 $$(ps aux | grep '[p]ython server.py' | awk '{print $$2}') 
	@echo "stoped"

clean:
	@find -name nohup.out -exec rm -f {} \;
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf 
	@find -name .cache | xargs rm -rf 
	
check:
	@ps axu | grep server-main.py



backupfile = "rpc-$(shell date +"%Y-%m-%d-%H-%M-%S" ).tar.gz"
bak:clean
	@tar czvf "../"$(backupfile) ../rpc  
	@mv ../rpc-*.tar.gz ../backup
	@echo "----back up successed!-----"

