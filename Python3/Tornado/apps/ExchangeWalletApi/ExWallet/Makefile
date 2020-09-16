
ifeq (, $(shell which python ))
  $(error "PYTHON=$(PYTHON) not found in $(PATH)")
endif


PYTHON_VERSION_MIN=3.7
PYTHON_VERSION=$(shell python -c 'import sys; print("%d.%d"% sys.version_info[0:2])' )
PYTHON_VERSION_OK=$(shell python -c 'import sys;\
  print(int(float("%d.%d"% sys.version_info[0:2]) >= $(PYTHON_VERSION_MIN)))' )

#ifeq ($(PYTHON_VERSION_OK),0)
#  $(error "ERROR: need python must  >= $(PYTHON_VERSION_MIN)")
#endif



deps:
	@sudo yum -y install python-devel
	@sudo yum -y install epel-release
	@sudo yum -y install python-pip
	@pip install --upgrade pip
	@pip install --upgrade setuptools
	@sudo yum install -y setuptool
	@sudo yum -y install gcc gcc-c++ kernel-devel
	@sudo yum -y install openssl-devel
	@pip install -r requirements.txt




#for dev
start-testnet:clean
	@echo "loading service......"

	@rm -rf constant.py
	@cp -f ./config/testnet  constants.py
	@nohup python -u server.py   >  server.log   2>&1 &

	@sleep 5s
	@echo "start successed processes count:"  $$(ps aux | grep '[p]ython -u server.py' | wc -l)
	@echo "testing...   curl http://127.0.0.1:9000/ping  "
	@sleep 5s
	@echo  $$(curl  http://127.0.0.1:9000/ping)

start-mainnet:clean
	@echo "loading service......"

	@rm -rf constant.py
	@cp -f ./config/mainnet  constants.py
	@nohup python -u server.py   >  server.log   2>&1 &

	@sleep 5s
	@echo "start successed processes count:"  $$(ps aux | grep '[p]ython -u server.py' | wc -l)
	@echo "testing...   curl http://127.0.0.1:9000/ping  "
	@sleep 5s
	@echo  $$(curl  http://127.0.0.1:9000/ping)



stop: 
	@kill -9 $$(ps aux | grep '[p]ython -u server.py' | awk '{print $$2}')
	@echo "stoped"

clean:
	@rm -rf *.log
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf 
	@find -name .cache | xargs rm -rf 
	
check:
	@ps axu | grep server.py



backupfile = "ExWallet-$(shell date +"%Y-%m-%d-%H-%M-%S" ).tar.gz"
bak:clean
	@tar czvf "../"$(backupfile) ../ExWallet
	@mv ../ExWallet-*.tar.gz ../backup
	@echo "----back up successed!-----"

