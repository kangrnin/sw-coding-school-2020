from flask import Flask, render_template
from flask_restful import Resource, Api

import json

import config
import indexer
from typeahead import get_typeahead
from path import abs_path

app = Flask(__name__)

api = Api(app)

class Info(Resource):
   def get(self):
      with open(abs_path(config.path_info), 'r', encoding='UTF8') as f:
         info = json.load(f)
         info['version'] = config.version
         info['prefix_length'] = config.prefix_length
         info['pq_size'] = config.pq_size
         return info

class Health(Resource):
   def get(self):
      return True

class Typeahead(Resource):
   def get(self, prefix):
      return get_typeahead(prefix)

class Reload(Resource):
   def post(self):
      indexer.index()

class Index(Resource):
   def post(self, prefix):
      with open(abs_path(config.path_prefix_index), 'r') as f:
         lines = f.readlines()
      with open(abs_path(config.path_prefix_index), 'w') as f:
         for line in lines:
            if line.strip("\n") != prefix:
               f.write(line)

   def delete(self, prefix):
      word_count = dict()
      with open(abs_path(config.path_word_count), 'r') as f:
         word_count = json.load(f)

      del word_count[prefix]
      with open(abs_path(config.path_word_count), 'w') as f:
         f.write(json.dumps(word_count))
      
      indexer.make_prefix()

api.add_resource(Info, '/info')
api.add_resource(Health, '/healthcheck')
api.add_resource(Typeahead, '/search/<string:prefix>')
api.add_resource(Reload, '/admin/index/reload')
api.add_resource(Index, '/admin/index/<string:prefix>')

@app.route('/')
def mainpage():
   return render_template('index.html')

if __name__ == "__main__":
   app.run(debug=True, host=config.host_addr, port=config.port_num)