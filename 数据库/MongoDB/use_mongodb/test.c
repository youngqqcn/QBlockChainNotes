#include <bson.h>
#include <mongoc.h>
#include <stdio.h>

int
main (int   argc, char *argv[])
{
	mongoc_client_t *client;
	mongoc_collection_t *collection;
	bson_error_t error;
	bson_oid_t oid;
	bson_t *doc;

	mongoc_init ();

	client = mongoc_client_new ("mongodb://localhost:27017/?appname=insert-example");
	collection = mongoc_client_get_collection (client, "mydb", "mycoll");

	doc = bson_new ();
	bson_oid_init (&oid, NULL);
	BSON_APPEND_OID (doc, "_id", &oid);
	BSON_APPEND_UTF8 (doc, "hello", "world");
	BSON_APPEND_UTF8 (doc, "name", "yqq");
	BSON_APPEND_UTF8 (doc, "age", "23");
	BSON_APPEND_UTF8 (doc, "addr", "shenzhen");

	if (!mongoc_collection_insert (collection, MONGOC_INSERT_NONE, doc, NULL, &error)) {
		fprintf (stderr, "%s\n", error.message);
	}

	bson_destroy (doc);
	mongoc_collection_destroy (collection);
	mongoc_client_destroy (client);
	mongoc_cleanup ();

	return 0;
}
