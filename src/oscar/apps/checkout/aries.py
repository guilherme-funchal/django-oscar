import json
import threading
import subprocess
import time
from django.db import connection
import requests
import os.path
from django.conf import settings


host = settings.REST_ARIES['HOST']
port = settings.REST_ARIES['PORT']
wallet_prefix = settings.REST_ARIES['WALLET_PREFIX']
wallet_webhook_urls = settings.REST_ARIES['WALLET_WEBHOOK_URLS']
wallet_pass = settings.REST_ARIES['WALLET_PASS']
serviceEndpoint = settings.REST_ARIES['SERVICEENDPOINT']
endpoint = host + ":" + port

def check_subwallet_exist(email_user):
#Check if subwallet in Hyperledger Aries exist        
    value = None   
    connection = None
    
    try:
        response = requests.get(
            endpoint
            + "/multitenancy/wallets?wallet_name=" + wallet_prefix + "."+ email_user,
        )
        response.raise_for_status()
        connection = response.json()
                        
    except:
        raise    
    finally:    
        value = len(connection['results'])    
    #If subwallet doesn't exist create    
        if value == 0:
            create_subwallet(email_user)
            wallet_id_user =  get_wallet_id(email_user)
            token_user = get_token(wallet_id_user)
            create_local_did(token_user)
            
        return connection


def create_subwallet(email_user):     
#Create subwallet in Hyperledger Aries with email adress   

    json_model = {
        "key_management_mode": "managed",
        "label": email_user,
        "wallet_dispatch_type": "default",
        "wallet_key": wallet_pass,
        "wallet_name": wallet_prefix + "." + email_user,
        "wallet_type": "indy",
        "wallet_webhook_urls": [wallet_webhook_urls]
    }
    
    connection = None
    token = None
    connection = None
    endpoint = host + ":" + port 
    
    try:
        response = requests.post(
            endpoint
            + "/multitenancy/wallet",
            json.dumps(json_model)
        )
        response.raise_for_status()
        connection = response.json()
                        
    except:
        raise    
    finally:             
        return connection

def create_connection(email_user):
    #   This function check connecions in Hyperledger Aries between  users
    tmp = None
    email_user = str(email_user)
    invite = None
    value = None
    
    wallet_id_user =  get_wallet_id(email_user)
    token_user = get_token(wallet_id_user)
    
    wallet_id_ecommerce = get_wallet_id(settings.REST_ARIES['EMAIL_ECOMMERCE'])
    token_ecommerce = get_token(wallet_id_ecommerce)
    
    connection = check_connection(settings.REST_ARIES['EMAIL_ECOMMERCE'], token_user)
    
    
    value = len(connection['results']) 
    
    if value == 0:    
        connection = create_invite(settings.REST_ARIES['EMAIL_ECOMMERCE'], token_ecommerce)
    
        id = connection["invitation"]["@id"]
        recipientKeys = connection["invitation"]["recipientKeys"]

        connection = accept_invite(settings.REST_ARIES['EMAIL_ECOMMERCE'], token_user, id, recipientKeys)


def create_invite(email_user, token):
    #   This function create invitation in Hyperledger Aries between to connect users

    created_by = str(email_user)
    
    json_model = {
        "my_label": created_by
    }

    header = {'Authorization': 'Bearer ' + token}
    
    did = None
    connection = None

    try:
        response = requests.post(
            endpoint
            + "/connections/create-invitation",
            json.dumps(json_model),
            headers=header
        )

        response.raise_for_status()
        connection = response.json()

    except:
        raise
    finally:
        return connection

def check_connection(email, token):
    #   This function create invitation in Hyperledger Aries between to connect users

    header = {'Authorization': 'Bearer ' + token}
    
    did = None
    connection = None
    
    try:
        response = requests.get(
            endpoint
            + "/connections?alias=" + email,
            headers=header
        )
        response.raise_for_status()
        connection = response.json()

    except:
        raise
    finally:
        return connection



def accept_invite(created_by, token_creator, id, recipientKeys):
    #   This function create connections in Hyperledger Aries between users from invites 

    service_endpoint = settings.REST_ARIES['SERVICEENDPOINT']
    created_by = str(created_by)

    json_model = {
            "@id": id,
            "label": created_by,
            "recipientKeys": recipientKeys,
            "serviceEndpoint": service_endpoint
    }

    token_user = token_creator

    header = {'Authorization': 'Bearer ' + token_user, 'accept': 'application/json', 'Content-Type': 'application/ld+json'}

    did = None
    connection = None

    url = "/connections/receive-invitation?alias=" + created_by

    try:
        response = requests.post(
            endpoint
            + url,
            json.dumps(json_model),
            headers=header
        )

        response.raise_for_status()
        connection = response.json()

    except:
        raise
    finally:
        return connection
    

def get_wallet_id(email_user):
    #Check if subwallet in Hyperledger Aries exist         
    connection = None
    did = None
    
    try:
        response = requests.get(
            endpoint
            + "/multitenancy/wallets?wallet_name=" + wallet_prefix + "." + email_user,
        )
        response.raise_for_status()
        connection = response.json()
        did = connection["results"][0]["wallet_id"]
                        
    except:
        raise    
    finally:    
        return did

def get_token(wallet_id):
    #Check if subwallet in Hyperledger Aries exist        
    value = None   
    connection = None
    token = None
    
    try:
        response = requests.post(
            endpoint
            + "/multitenancy/wallet/" + wallet_id + "/token",
        )
        response.raise_for_status()
        connection = response.json()
        token = connection["token"]
                        
    except:
        raise    
    finally:    
        return token
    
def create_local_did(token_user):
        
    json_model = {
    "method": "key",
    "options": {
        "key_type": "bls12381g2"
        }
    }
    token_user = str(token_user)
    
    header = {'Authorization': 'Bearer ' + token_user}
    
    did = None
    connection = None    
      
    try:
        response = requests.post(
            endpoint
            + "/wallet/did/create",
            json.dumps(json_model),
            headers=header
        )
        
        response.raise_for_status()
        connection = response.json()
        
        did = connection["result"]["did"]
                    
    except:
        raise    
    finally:             
        return did
