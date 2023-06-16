from pymongo import MongoClient, ASCENDING, DESCENDING
from pprint import pprint
import random
import time
import pandas as pd


class DB:

    def __init__(self, ip='127.0.0.1', port=27017, database='plywood'):
        self.client = MongoClient( 'mongodb://{}:{}/'.format(ip, port))
        self.knowledge_base = self.client[database]

    def add(self, theme, element):
        result = self.knowledge_base[theme].insert_one(element)
        return result.inserted_id

    def delete(self, theme, element):
        self.knowledge_base[theme].delete_one(element)

    def show(self, theme):
        for obj in list(self.knowledge_base[theme].find({})):
            print(obj)

    def clear(self, theme):
        for obj in list(self.knowledge_base[theme].find({})):
            self.delete(theme=theme, element=obj)

    def find(self, theme, named_entities, answer_field):
        tmp = answer_field
        answer_field = dict()
        for element in tmp:
            answer_field[element] = 1
        answer_field['_id'] = 0
        
        out = []
        if named_entities != {}:
            for key in named_entities.keys():
                if isinstance(named_entities[key], list):
                    for element in named_entities[key]:
                        out.append({key : element})
                else:
                    out.append({key : named_entities[key]})

            named_entities = {'$and' : out}

        result = list(self.knowledge_base[theme].find(named_entities, answer_field))
        return result


    def find_manual(self, theme, named_entities, answer_field):
        tmp = answer_field
        answer_field = dict()
        for element in tmp:
            answer_field[element] = 1
        answer_field['_id'] = 0        
        result = list(self.knowledge_base[theme].find(named_entities, answer_field))
        return result


    def find_limit(self, theme, named_entities, answer_field, limit):
        tmp = answer_field
        answer_field = dict()
        for element in tmp:
            answer_field[element] = 1
            sort_fild = element
        answer_field['_id'] = 0
        result = list(self.knowledge_base[theme].find(named_entities, answer_field).sort([(sort_fild, -1)]).limit(limit))
        return result


    def count_arr_el(self, theme, named_entities_match, named_entities_group):
        tmp = named_entities_group.copy()
        for key in tmp.keys():
            named_entities = [{"$match": named_entities_match}, {"$unwind":"${}".format(key)}, {"$group":{"_id":"${}".format(key), "count": {"$sum": 1}}}]
            result = list(self.knowledge_base[theme].aggregate(named_entities))

            #pprint(result)

            #for el in result:
            #    if el['_id'] == tmp[key]:
            #        return el['count']

            return result


if __name__ == '__main__':

    #db = DB(ip='192.168.2.95', port=27017, database='plywood')
    db = DB(ip='127.0.0.1', port=28818, database='timber')
    theme = 'rskr'

    db.knowledge_base[theme].create_index([('sec_time', DESCENDING)])
    db.clear(theme) 

