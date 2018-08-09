from time import time
import json
import hashlib

from uuid import uuid4
from flask import Flask
from textwrap import dedent


class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []

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

        return self.last_block['index'] + 1


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
    return "Hard work"


@app.route("/transaction/new", methods=['POST'])
def new_transaction():
    return "Adding transaction"

@app.route("/chain", methods=['GET'])
def all_chain():
    return "List of block"

app.run(host='0.0.0.0', port=4802)
