
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

export PYTHONPATH=/data/PaymentGateway/PG_Withdraw/


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




start:clean
	@echo 请注意!当前环境为 ${ENV_NAME}
	@echo "loading service......"

	@nohup python3 -u src/api/withdraw_api.py   >  withdraw_api.log   2>&1 &
	@nohup python3 -u src/consumers/eth_erc20_consumer_main.py   >  eth_erc20_consumer_main.log   2>&1 &
	@nohup python3 -u src/consumers/htdf_consumer_main.py   >  htdf_consumer_main.log   2>&1 &
	@nohup python3 -u src/consumers/btc_consumer_main.py   >  btc_consumer_main.log   2>&1 &
	@nohup python3 -u src/monitor/timing_monitoring.py   >  timing_monitoring.log   2>&1 &
	@nohup python3 -u src/monitor/tx_monitor_notify.py   >  tx_monitor_notify.log  2>&1 &
	@nohup python3 -u src/monitor/timing_monitoring_for_badguys.py   >  timing_monitoring_for_badguys.log  2>&1 &

	@sleep 5s
	@echo "start successed processes count:"  $$(ps aux | grep '[p]ython -u src/api/withdraw_api.py'  | wc -l)
	@echo "testing...   curl http://127.0.0.1:59002/ping  "
	@sleep 5s
	@echo  $$(curl  http://127.0.0.1:59002/ping)


#要先杀子进程
stop:
	@kill $$(ps aux | grep '[p]ython3 -u src/api/withdraw_api.py' | awk '{print $$2}' | awk '{a[i++]=$$0} END {while(i--) print a[i]}')
	@kill -9  $$(ps aux | grep '[p]ython3 -u src/consumers/eth_erc20_consumer_main.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/consumers/htdf_consumer_main.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/consumers/btc_consumer_main.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/monitor/timing_monitoring.py'  | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/monitor/tx_monitor_notify.py'  | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/monitor/timing_monitoring_for_badguys.py'  | awk '{print $$2}')
	@echo "stoped"

stop-api:
	@kill $$(ps aux | grep '[p]ython3 -u src/api/withdraw_api.py' | awk '{print $$2}' | awk '{a[i++]=$$0} END {while(i--) print a[i]}')

clean:
	@rm -rf *.log
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf
	@find -name .cache | xargs rm -rf

check:
	@ps axu | grep withdraw_api.py

