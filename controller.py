from flask import Response, request
from flask_sqlalchemy import SQLAlchemy
from model import Host
from alert import Alert
from conn import ConnMySQL
import os
import json, hashlib
import time
import logging


class Controller:
    
    # reservado apara adição estática de cabeçalhos de segurança
    headers = {'Access-Control-Allow-Origin': '*'}

    def __init__(self, db: SQLAlchemy):
        self.db = db

    """procurar host no banco de dados usuário pela api-key
    """
    def host_by_apikey(self, api_key: str) -> Host or None:
        host = self.db.session.query(Host).filter_by(apikey=api_key).first()
        return host

    """procurar host no banco de dados usuário pelo hostname
    """
    def host_by_hostname(self, hostname: str) -> Host or None:
        host = self.db.session.query(Host).filter_by(hostname=hostname).first()
        return host

    """autenticador de usuário, caso exista e as informações confiram
    no banco de dados requisição poderá prosseguir, caso contrario será exibido uma mensagem
    de erro para o cliente
    Returns:
        [dict] -- [resposta com status (true/false) e código do error]
    """
    def guard(self) -> dict:
        hostname: str = request.headers.get('hostname')
        apikey: str = request.headers.get('api-key')
        ip: str = request.remote_addr

        if (hostname is None) or (apikey is None):
            return {'status': False, 'code': 1}

        info = (hostname+apikey+ip).encode('utf-8')
        # cálculo de hash com informações do agent
        sha = hashlib.sha1(info).hexdigest()

        # debug
        # logging.warning('request from "%s" with hostname "%s"' % (ip, hostname))

        host: Host or None = self.host_by_apikey(api_key=apikey)

        if host is None:
            return {'status': False, 'code': 3}

        hostname_is_equal: bool = host.hostname == hostname
        apikey_is_equal: bool = host.apikey == apikey
        ip_is_equal: bool = host.ip == ip

        # host.sha é o cálculo da soma em string de todos os campos
        # na tabela de host, para que mesmo que o atacante tenha o api-key vai garantir
        # que só funcione a requisição se for do host cadastrado
        sha_is_equal: bool = host.sha == sha
        
        if all([hostname_is_equal, apikey_is_equal, ip_is_equal, sha_is_equal]):
            return {'status': True, 'host': host}
        
        return {'status': False, 'code': 2}

    """cadastra novo agente no banco de dados
    """
    def new_agent(self, hostname: str, api_key: str, ip: str)-> dict:
        if not self.db.session.query(Host).filter_by(hostname=hostname).count() < 1:
            return {'code': 1}

        info = (hostname+api_key+ip).encode('utf-8')
        # cálculo de hash com informações do agent
        sha = hashlib.sha1(info).hexdigest()

        host_temp = Host(hostname=hostname, apikey=api_key,
            ip=ip, sha=sha)
        logging.warning(' - user "%s:%s" add in database SQLite' % (host_temp.hostname, host_temp.ip))
        self.db.session.add(host_temp)

        try:
            self.db.session.commit()
            return {'code': 0}
        except Exception as err:
            self.db.session.rollback()
            logging.error(' - error to add user in database: %s' % err)
        return {'code': 2}

    """deve ser chamada se forma assíncrona com threading para salvar logs
    dos agentes no banco de dados MySQL
    """
    @staticmethod
    def save(path, ip, conn):
        time.sleep(10)

        if not os.path.isfile(path):
            logging.error(' - path file "%s" not found' % path)
            return False

        f = open(path, 'r')
        lines = list(map(lambda x: x.replace('\n',''), f.readlines()))
        for line in lines:
            alert = Alert.create_alert(ip, line)
            if not conn.insert(alert.alert()):
                logging.warning(' - could not add alert, maybe it already exists in the database')

    """reposta json customizada com headers adicionais
    Returns:
        [Response] -- [resposta http]
    """
    @staticmethod
    def jsonify(content: 'str or dict', status_code: int = 200) -> Response:
        if isinstance(content, dict): content = json.dumps(content)
        return Response(content, mimetype='application/json', status=status_code, 
            headers=Controller.headers)