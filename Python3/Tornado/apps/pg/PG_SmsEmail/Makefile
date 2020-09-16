
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


export PYTHONPATH=/data/PaymentGateway/PG_SmsEmail/

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
	@nohup python3 -u  src/sms_consumer_main.py  >  sms_consumer_main.log 2>&1 &
	@echo  "started"


stop:
	@kill -9 $$(ps aux | grep '[p]ython3 -u src/sms_consumer_main.py' | awk '{print $$2}')
	@echo "stoped"

clean:
	@rm -rf *.log
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf
	@find -name .cache | xargs rm -rf

check:
	@ps axu | grep server.py


