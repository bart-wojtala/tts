from database_client import DatabaseClient

db_client = DatabaseClient()
msgs = db_client.get_all_generated_messages()
for i, m in enumerate(msgs):
    print(m.get('text'))