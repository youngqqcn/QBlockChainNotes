
ifeq (, $(shell which python3 ))
  $(error "PYTHON=$(PYTHON) not found in $(PATH)")
endif


PYTHON_VERSION_MIN=3.7
PYTHON_VERSION=$(shell python3 -c 'import sys; print("%d.%d"% sys.version_info[0:2])' )
PYTHON_VERSION_OK=$(shell python3 -c 'import sys;\
  print(int(float("%d.%d"% sys.version_info[0:2]) >= $(PYTHON_VERSION_MIN)))' )

ifeq ($(PYTHON_VERSION_OK),0)
  $(error "ERROR: need python must  >= $(PYTHON_VERSION_MIN)")
endif

export PYTHONPATH=/data/PaymentGateway/PG_Deposit/


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
start:clean
	@echo 请注意!当前环境为 ${ENV_NAME}
	@echo "loading service......"
	@nohup python3 -u src/api/deposit_api.py   >  deposit_api.log   2>&1 &
	@nohup python3 -u src/scanners/eth_scanner_main.py   >  eth_scanner_main.log   2>&1 &
	@nohup python3 -u src/scanners/htdf_scanner_main.py   >  htdf_scanner_main.log   2>&1 &
	@nohup python3 -u src/scanners/btc_scanner_main.py   >  btc_scanner_main.log   2>&1 &

	@sleep 5s
	@echo "start successed processes count:"  $$(ps aux | grep '[p]ython3 -u src/api/deposit_api.py'  | wc -l)
	@echo "testing...   curl http://127.0.0.1:59001/ping  "
	@sleep 5s
	@echo  $$(curl  http://127.0.0.1:59001/ping)

stop:
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/api/deposit_api.py'  | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/scanners/htdf_scanner_main.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/scanners/eth_scanner_main.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/scanners/btc_scanner_main.py' | awk '{print $$2}')
	@echo "stoped"

clean:
	@rm -rf *.log
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf
	@find -name .cache | xargs rm -rf

check:
	@ps axu | grep deposit_api.py


