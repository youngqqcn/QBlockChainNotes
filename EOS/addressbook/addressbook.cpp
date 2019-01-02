#include <eosiolib/eosio.hpp>

using namespace eosio;

class [[eosio::contract]] addressbook : public eosio::contract {  //使用辅助属性，让ABI生成器提取参数信息和结构体信息

	public:
		using contract::contract;
		addressbook(name receiver, name code, datastream<const char*> ds):contract(receiver, code, ds){}


		[[eosio::action]]   //使用辅助属性，让ABI生成器提取参数信息和结构体信息
		void upsert(name user, std::string first_name, std::string last_name, std::string street, std::string city, std::string state)
		{
			require_auth(user);

			address_index addresses(_code, _code.value);

			auto iterator = addresses.find(user.value);

			if(iterator == addresses.end())
			{
				//如果用户不存在， 则创建用户
				addresses.emplace(user, [&](auto &row){
						row.key = user;
						row.first_name = first_name;
						row.last_name = last_name;
						row.street = street;
						row.city = city;
						row.state = state;
						});
			}
			else
			{
				//如果用户已经存在则修改信息
				//std::string changes;
				addresses.modify(iterator, user, [&]( auto& row ) {
						row.key = user;
						row.first_name = first_name;
						row.last_name = last_name;
						row.street = street;
						row.city = city;
						row.state = state;
						});

			}
		}


		[[eosio::action]]   //使用辅助属性，让ABI生成器提取参数信息和结构体信息
		void erase(name user)
		{
			require_auth(user);
			address_index addresses(_self, _code.value);
			auto iterator = addresses.find(user.value);
			eosio_assert(iterator != addresses.end(), "要删除的数据不存在");
			addresses.erase(iterator);
		}

	private: 

		  
		//struct person;
		struct [[eosio::table]] person{ //使用辅助属性，让ABI生成器提取参数信息和结构体信息
			name key;
			std::string first_name;
			std::string last_name;
			std::string street;
			std::string city;
			std::string state;

			uint64_t primary_key() const{return key.value;}
		};

		typedef eosio::multi_index<"people"_n, person> address_index;

};


//这个宏定义是给wasm编译器用的，用来将一个调用与合约中的具体函数关联映射起来
EOSIO_DISPATCH(addressbook, (upsert)(erase))





