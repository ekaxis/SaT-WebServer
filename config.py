from flask import Flask
import os, logging, sys
from os.path import join, dirname
from dotenv import load_dotenv
from conn import ConnMySQL

#
# dependências do python - pip
# python-dotenv==0.13.0
# Flask==1.1.2
# Flask-SQLAlchemy==2.4.3
# 
# versão feita e testada - Python 3.8.2 (x86-64)
# pip install -r requirements.txt
#
try: os.mkdir(join(join(dirname(__file__), 'db')))
except: pass
try: os.mkdir(join(join(dirname(__file__), 'files')))
except: pass
try: os.mkdir(join(join(dirname(__file__), 'log')))
except: pass
# configurações logging (DEBUG)
format_logging = '%(asctime)s %(levelname)s\t %(message)s' # 17/05/2020 17:05:05 INFO	  * Restarting with stat
datefmt = '%d/%m/%Y %H:%I:%M'  # 27/04/2020 20:49
filename_log = join(join(dirname(__file__), 'log'), 'warn.log') # absolute path
logging.basicConfig(level=logging.DEBUG, filename=filename_log, format=format_logging, filemode='a+', datefmt=datefmt)
# Flask app configurações
app = Flask(__name__) # global variable (main)
# carregar variáveis de ambiente
dotenv_path = join(dirname(__file__), '.env')
if not os.path.isfile(dotenv_path):
    logging.error('.env file not found, try cp .env.examp .env'); sys.exit(0)
load_dotenv(dotenv_path=dotenv_path)
UPLOAD_FOLDER = join(dirname(__file__), os.environ.get('UPLOAD_FOLDER'))
KEY_MASTER = os.environ.get('KEY_MASTER')
# configurações Flask App
if os.environ.get('SECRET_KEY') is None:
    logging.error('set "SECRET KEY" in .env file'); sys.exit(0)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # do arquivo .env
# config run server development
HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')
DEBUG = os.environ.get('DEBUG')
# configuração de banco de dados mysql
HOST_DB = os.environ.get('HOST_DB')
USER_DB = os.environ.get('USER_DB')
PASS_DB = os.environ.get('PASS_DB')
PORT_DB = os.environ.get('PORT_DB')
DATABASE = os.environ.get('DATABASE')
# criar objeto ConnMySQL
conn = ConnMySQL(USER_DB, PASS_DB, HOST_DB, DATABASE)
# mensagens de error possíveis para resposta da api
ERROR = {
    1: "'hostname' or/and 'api-key' not found in headers",
    2: 'unauthorized host to perform operation',
    3: 'host not registered in the database',
    4: 'file not found in request',
    5: 'file already exists',
    6: 'incorrect request',
    7: 'data json not found',
    8: 'sorry, user does not exist'
}
