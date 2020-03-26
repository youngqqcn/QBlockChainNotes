#!coding:utf8

#author:yqq
#date:2019/12/27 0027 10:17
#description:

import eospy
import eospy.cleos
import eospy.keys
from  pprint import pprint

class MyEOSCleosEx( eospy.cleos.Cleos ):

    def __init__(self, url='http://localhost:8888', version='v1'):
        ''' '''
        eospy.cleos.Cleos.__init__(self, url=url, version=version)

    #抵押换取资源
    #可以为别人抵押(赎回后的EOS归别人所有)
    def buy_resource(self, payer, payer_privkey, recv_acc_name
                     , stake_net='10.0000 EOS', stake_cpu='10.0000 EOS', ramkb=10, permission='active',
                     transfer=False, broadcast=True, timeout=30):

        # create buyrambytes trx
        buyram_data = self.abi_json_to_bin('eosio', 'buyrambytes',
                                           {'payer': payer, 'receiver': recv_acc_name, 'bytes': ramkb * 1024})
        buyram_json = {
            'account': 'eosio',
            'name': 'buyrambytes',
            'authorization': [
                {
                    'actor': payer,
                    'permission': permission
                }],
            'data': buyram_data['binargs']
        }


        # create delegatebw
        delegate_data = self.abi_json_to_bin('eosio', 'delegatebw',
                                             {'from': payer, 'receiver': recv_acc_name, 'stake_net_quantity': stake_net,
                                              'stake_cpu_quantity': stake_cpu, 'transfer': transfer})
        delegate_json = {
            'account': 'eosio',
            'name': 'delegatebw',
            'authorization': [
                {
                    'actor': payer,
                    'permission': permission
                }],
            'data': delegate_data['binargs']
        }

        trx = {
            # "actions":[buyram_json, delegate_json]
            "actions":[ delegate_json]
        }
        # push transaction
        return self.push_transaction(trx, payer_privkey, broadcast=broadcast, timeout=timeout)




def delegate_for_other():
    cl = MyEOSCleosEx(url='http://jungle2.cryptolions.io:80')
    key = eospy.keys.EOSKey('5JgJo2Wo2hAqLzqnzCUSKiBdbfyDEdPFNdrYF7crqkVsSPd7e8o')  # hetbitraeqhj
    retinfo = cl.buy_resource('hetbitraeqhj', key, 'hetbitesteos', transfer=True)
    pprint(retinfo)


def  my_create_acct():
    cl = MyEOSCleosEx(url='https://api.eosnewyork.io')
    key = eospy.keys.EOSKey('5JiQvUV4s2B4UVJhnr71V5z95531uZaPCYrdPRK8cQCUhcDHW2E')
    # owner_key = 'EOS8NNkboRde8LYJpU9bwbE9AbYGjdyfGP8R16WvuQ2XRKYRLywaa'
    # retinfo = cl.create_account(creator='happyyoungqq', creator_privkey=key, acct_name='hetbinehpckf', owner_key=owner_key
    #                             ,active_key=owner_key, stake_net='0.5000 EOS', stake_cpu='20.0000 EOS',
    #                             ramkb=40, permission='active', transfer=True)

    # retinfo = cl.create_account(creator='happyyoungqq', creator_privkey=key, acct_name='hetbimcpgqnd', owner_key=owner_key
    #                             ,active_key=owner_key, stake_net='10.0000 EOS', stake_cpu='470.0000 EOS',
    #                             ramkb=100, permission='active', transfer=True)

    owner_key = 'EOS8WUxrZ1PpihB8JHRymS5W8rcAqnR3383RLvL4ZF9Qrmgcjwqu9'
    retinfo = cl.create_account(creator='happyyoungqq', creator_privkey=key, acct_name='hetbijzekvrm',
                                owner_key=owner_key
                                , active_key=owner_key, stake_net='10.0000 EOS', stake_cpu='486.0000 EOS',
                                ramkb=100, permission='active', transfer=True)
    pprint(retinfo)


def main():


    my_create_acct()

    # cl = MyEOSCleosEx(url='http://jungle2.cryptolions.io:80')
    # cl = MyEOSCleosEx(url='https://api.eosnewyork.io')
    # key = eospy.keys.EOSKey('5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw')
    # key = eospy.keys.EOSKey('5JgJo2Wo2hAqLzqnzCUSKiBdbfyDEdPFNdrYF7crqkVsSPd7e8o') #hetbitraeqhj
    # key = eospy.keys.EOSKey('5JiQvUV4s2B4UVJhnr71V5z95531uZaPCYrdPRK8cQCUhcDHW2E')
    # retinfo = cl.buy_resource('hetbitraeqhj', key , 'hetbitesteos' , transfer=True )
    # retinfo = cl.buy_resource('happyyoungqq', key , 'yijiayi12345', stake_net='0.1000 EOS' , stake_cpu='0.0000 EOS' )

    # retinfo = cl.buy_resource('happyyoungqq', key , 'happyyoungqq', stake_net='0.0000 EOS' , stake_cpu='100.0000 EOS' )


    # owner_key = 'EOS8NNkboRde8LYJpU9bwbE9AbYGjdyfGP8R16WvuQ2XRKYRLywaa'
    # retinfo = cl.create_account(creator='happyyoungqq', creator_privkey=key, acct_name='hetbinehpckf', owner_key=owner_key
    #                             ,active_key=owner_key, stake_net='0.5000 EOS', stake_cpu='20.0000 EOS',
    #                             ramkb=40, permission='active', transfer=True)


    # cl.create_account('happyyoungqq')





    pass


if __name__ == '__main__':

    main()