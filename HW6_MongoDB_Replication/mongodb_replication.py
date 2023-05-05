import time
import argparse
from faker import Faker
from datetime import datetime
from pymongo import MongoClient


NODE_ADDRESSES = ['mongo-node1:27017', 'mongo-node2:27017', 'mongo-node3:27017']


def write_to_db(write_concern, journaled, write_timeout_ms=0, n_records_to_write=1000):
    fake = Faker()

    client = MongoClient(f'mongodb://{",".join(NODE_ADDRESSES)}/test?replicaSet=rs0&w={write_concern}&journal={str(journaled).lower()}&wTimeoutMS={write_timeout_ms}')
    collection = client.get_database('test').get_collection('dd_hw6')
    print('Connected to the DB')

    start_time = time.time()
    now = datetime.now()
    for i in range(n_records_to_write):
        new_record = {
            "name": fake.name(),
            "address": fake.address(),
            "country": fake.country(),
            "record_create_date_time": now.strftime("%m/%d/%Y, %H:%M:%S")
        }
        collection.insert_one(new_record)

    end_time = time.time()

    print(f'Everything is written. Execution time: {end_time - start_time}.')


def read_from_db(read_preference):
    client = MongoClient(f'mongodb://{",".join(NODE_ADDRESSES)}/test?replicaSet=rs0&readPreference={read_preference}')
    collection = client.get_database('test').get_collection('dd_hw6')
    print('Connected to the DB')

    start_time = time.time()

    print('Records that contain the "Poland" country')
    for x in collection.find({"country": 'Poland'}, {"_id": 0, "name": 1, "address": 1, "country": 1}):
        print(x)

    end_time = time.time()

    print(f'Everything is written. Execution time: {end_time - start_time}.')


def select_with_read_concern(read_concern):
    client = MongoClient(f'mongodb://{",".join(NODE_ADDRESSES)}/test?replicaSet=rs0&readConcernLevel={read_concern}')
    collection = client.get_database('test').get_collection('dd_hw6')
    print('Connected to the DB')

    start_time = time.time()
    print('Top 10 records')
    for x in collection.find({}, {"_id": 0, "name": 1, "address": 1, "country": 1}).limit(10):
        print(x)

    end_time = time.time()

    print(f'Everything is written. Execution time: {end_time - start_time}.')


if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-w", "--write_concern", required=False)
    parser.add_argument("-wt", "--write_timeout_ms", required=False)
    parser.add_argument("-rp", "--read_preference", required=False)
    parser.add_argument("-r", "--read_concern", required=False)

    # Read arguments from command line
    args = parser.parse_args()
    if args.write_concern is not None:
        write_concern, journaled = None, None
        if args.write_concern == 'unacknowledged':
            write_concern = '0'
            journaled = False
        elif args.write_concern == 'acknowledged':
            write_concern = '1'
            journaled = False
        elif args.write_concern == 'journaled':
            write_concern = '1'
            journaled = True
        elif args.write_concern == 'acknowledged_replica':
            write_concern = 'majority'
            journaled = False
        else:
            write_concern = args.write_concern
            journaled = False

        write_timeout_ms = args.write_timeout_ms if args.write_timeout_ms else 0
        write_to_db(write_concern, journaled, write_timeout_ms)

    elif args.read_preference is not None:
        read_from_db(args.read_preference)

    elif args.read_concern is not None:
        select_with_read_concern(args.read_concern)
