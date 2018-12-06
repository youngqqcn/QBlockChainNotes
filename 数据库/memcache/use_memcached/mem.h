#ifndef MEMCACHEDCLIENT
 
#define MEMCACHEDCLIENT 
 
#include <libmemcached/memcached.h>
#include<iostream>
#include<string.h>
#include<time.h>
#include <stdlib.h>
#include <stdio.h>
 
using std::string;
using std::cout;
using std::endl;
 
class MemCachedClient
{   
public:
        ~MemCachedClient()
        {
            memcached_free(memc);
        };
 
        MemCachedClient()
        {
            memcached_return rc;                                                                   
            memcached_server_st *server = NULL;
            memc = memcached_create(NULL);
            
            server =memcached_server_list_append(server, "127.0.0.1", 11211, &rc);
            rc=memcached_server_push(memc,server);                                         
 
            if (MEMCACHED_SUCCESS != rc){
                 cout <<"memcached_server_push failed! rc: " << rc << endl;
            }
 
            memcached_server_list_free(server);
        };
 
        int Insert(const char* key, const char* value,time_t expiration = 3)
        {
            if (NULL == key || NULL == value)
            {  
                return -1;
            }
			
            uint32_t flags = 0;
 
            memcached_return rc;
            rc = memcached_set(memc, key, strlen(key),value, strlen(value), expiration, flags);
 
            // insert ok
            if (MEMCACHED_SUCCESS == rc)
            {
                return 1;
            }
            else
            {
                return 0;
            }
        };
         
        
        string Get(const char* key)
        {
             if (NULL == key)
             {  
                return "no key";
             }
 
            uint32_t flags = 0;
 
            memcached_return rc;
 
            size_t value_length;
            char* value = memcached_get(memc, key, strlen(key), &value_length, &flags, &rc);
 
            // get ok
            if(rc == MEMCACHED_SUCCESS)
            {  
                return value;
            }
 
            return "no value";
        };
 
    private:
        memcached_st* memc;
};
 
#endif

