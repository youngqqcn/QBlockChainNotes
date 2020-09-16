
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


retart: stop start


start-testnet:
	@rm -rf ./config.py
	@cp ./config/testnet  ./config.py
	@nohup python -u ethscanner.py   >  log_eth.log  2>&1 &
	@nohup python -u usdpscanner.py   > log_usdp.log  2>&1 &
	@nohup python -u htdfscanner.py   > log_htdf.log  2>&1 &
	@nohup python -u hetscanner.py   >  log_het.log  2>&1 &
	@nohup python -u ripple/ripplescanner.py   >  log_xrp.log  2>&1 &
	@nohup python -u eos/eos_scanner.py   >  log_eos.log  2>&1 &
	@nohup python -u etc/ethscanner.py   >  log_etc.log  2>&1 &
	@nohup python -u xlm/xlm_scanner.py   >  log_xlm.log  2>&1 &
	@nohup python -u trx/trx_scanner.py   >  log_trx.log  2>&1 &
	@nohup python -u xmr/xmr_scanner.py   >  log_xmr.log  2>&1 &
	@echo "started, status:" $$(ps aux|grep '[p]ython -u .*scanner.*'|wc -l)"/10 running"





start-mainnet:
	@rm -rf ./config.py
	@cp ./config/mainnet ./config.py
	@nohup python -u ethscanner.py   >  log_eth.log   2>&1 &
	@nohup python -u usdpscanner.py   > log_usdp.log  2>&1 &
	@nohup python -u htdfscanner.py   > log_htdf.log  2>&1 &
	@nohup python -u hetscanner.py   >  log_het.log  2>&1 &
	@nohup python -u ripple/ripplescanner.py   >  log_xrp.log  2>&1 &
	@nohup python -u eos/eos_scanner.py   >  log_eos.log  2>&1 &
	@nohup python -u etc/ethscanner.py   >  log_etc.log  2>&1 &
	@nohup python -u xlm/xlm_scanner.py   >  log_xlm.log  2>&1 &
	#@nohup python -u trx/trx_scanner.py   >  log_trx.log  2>&1 &
	@nohup python -u xmr/xmr_scanner.py   >  log_xmr.log  2>&1 &
	@echo "started, status:" $$(ps aux|grep '[p]ython -u .*scanner.*'|wc -l)"/9 runing"



stop: 
	@kill -9 $$(ps aux | grep '[p]ython -u ethscanner.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython -u usdpscanner.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython -u htdfscanner.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython -u hetscanner.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython -u ripple/ripplescanner.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython -u eos/eos_scanner.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython -u etc/ethscanner.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython -u xlm/xlm_scanner.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython -u trx/trx_scanner.py' | awk '{print $$2}')
	@kill -9 $$(ps aux | grep '[p]ython -u xmr/xmr_scanner.py' | awk '{print $$2}')
	@echo "stoped"




clean:
	@rm -rf *.log
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf
	@find -name .cache | xargs rm -rf 


backup = "blockscanner-$(shell date +"%Y-%m-%d-%H-%M-%S" ).tar.gz"
bak:clean
	@tar czvf "../"$(backup) ../blockscanner  
	@mv ../blockscanner-*.tar.gz ../backup
	@echo "----back up successed!-----"

