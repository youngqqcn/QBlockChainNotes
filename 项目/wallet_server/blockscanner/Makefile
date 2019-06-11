retart: stop start


start-testnet:
	@rm -rf ./config.py
	@cp ./config/testnet  ./config.py
	@nohup /usr/bin/python  ethscanner.py &  > /dev/null
	@nohup /usr/bin/python  usdpscanner.py &  > /dev/null
	@nohup /usr/bin/python  htdfscanner.py &  > /dev/null

start-mainnet:
	@rm -rf ./config.py
	@cp ./config/mainnet ./config.py
	@nohup /usr/bin/python  ethscanner.py &  > /dev/null
	@nohup /usr/bin/python  usdpscanner.py &  > /dev/null
	@nohup /usr/bin/python  htdfscanner.py &  > /dev/null



stop: 
	@kill -9 $$(ps aux | grep '[p]ython ethscanner.py' | awk '{print $$2}') 
	@kill -9 $$(ps aux | grep '[p]ython usdpscanner.py' | awk '{print $$2}') 
	@kill -9 $$(ps aux | grep '[p]ython htdfscanner.py' | awk '{print $$2}') 
	@echo "stoped"

check:
	@ps axu | grep scanner.py


clean:
	@find -name nohup.out -exec rm -f {} \;
	@find -name "*.pyc" -exec rm -f {} \;
	@find -name __pycache__ | xargs rm -rf 
	@find -name .cache | xargs rm -rf 


backup = "blockscanner-$(shell date +"%Y-%m-%d-%H-%M-%S" ).tar.gz"
bak:clean
	@tar czvf "../"$(backup) ../blockscanner  
	@mv ../blockscanner-*.tar.gz ../backup
	@echo "----back up successed!-----"

