from time import time
import json
import hashlib

from uuid import uuid4
from flask import Flask, request
from flask.json import jsonify
from textwrap import dedent

from urllib.parse import urlparse
import requests




class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Creation du block initial (Genesis block)
        self.new_block(previous_hash = 1, proof = 100)


    def new_block(self, proof, previous_hash = None):
        # Creer un nouveau block dans la chaine

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block())
        }

        # Reset les transactions en attente
        self.current_transactions = []

        self.chain.append(block)
        return block


    def new_transaction(self, auteur, oeuvre):
        # Creer une nouvelle transaction dans la liste

        self.current_transactions.append({
            'auteur': auteur,
            'oeuvre': oeuvre,
            'time': time()
        })

        return self.last_block()['index'] + 1


    def proof_of_work(self, last_proof):
        # Boucle pour trouver la preuve
        proof = 0

        while not self.valid_proof(proof, last_proof):
            proof += 1

        return proof



    def valid_proof(self, proof, last_proof):
        # Verifie que la proof a bien été trouvée
        # hash(proof concat last_proof) commence par 00

        guess = "{}{}".format(proof, last_proof)
        guess_hash = hashlib.sha256(guess.encode("utf8")).hexdigest()
        return guess_hash[:2] == "00"


    def register_node(self, address):
        # Ajoute un noeud a la liste des noeuds dispo
        url = urlparse(address)
        self.nodes.add(url.netloc)


    def valid_chain(self, chain):
        # Verifie si une chaine est valide en la parcourant
        last_block, *tail = chain

        for block in tail:
            #Hash correcte
            if block['previous_hash'] != self.hash(last_block):
                return False

            #Proof of work correcte
            if not self.valid_proof(block['proof'], last_block['proof']):
                return False

            last_block = block

        return True



    def resolve_conflicts(self):
        # Decider quel blockchain garder dans notre reseau (plus longue)

        new_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            response = requests.get("http://{}/chain".format(node))

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # On remplace la chain si besoin
        if new_chain:
            self.chain = new_chain
            return True

        return False


    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def last_block(self):
        return self.chain[-1]

###################### BLOCKCHAIN API #####################


app = Flask(__name__)

#Identifier du noeud courant
node_id = str(uuid4()).replace("-", "")

blockchain = Blockchain()


@app.route("/mine", methods=["GET"])
def mine():

    last_block = blockchain.last_block()
    last_proof = last_block["proof"]
    proof = blockchain.proof_of_work(last_proof)

    # Ajout d'un reward pour le mineur dans les transactions

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "message": "You forged a new block :D",
        "block": block
    }

    return jsonify(response), 200



@app.route("/transaction/new", methods=['POST'])
def new_transaction():
    values = request.get_json()
    try:
        #Creation de la transaction
        block_index = blockchain.new_transaction(values['author'], values["artwork"])

        response = {
            'message': "Your artwork will be saved in block {}".format(block_index)
        }

        return jsonify(response), 200

    except KeyError as e:
        return "JSON key missing", 400



@app.route("/chain", methods=['GET'])
def all_chain():
    chain = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(chain), 200



@app.route('/nodes/register', methods=['POST'])
def register_node():
    nodes = request.get_json().get('nodes')

    if nodes is None:
        return "ERROR: No node provided", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': "New nodes added to network",
        'full_list': list(blockchain.nodes)
    }

    return jsonify(response), 200

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


app.run(host='0.0.0.0', port=4802)
