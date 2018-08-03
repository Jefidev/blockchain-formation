from time import time
import json
import hashlib

class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Creation du block initial (Genesis block)
        self.new_block(previous_hash = 1, proof = 100)


    def new_block(self, proof):
        # Creer un nouveau block dans la chaine

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': self.hash(self.last_block())
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

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hash.sha256(block_string).hexdigest()
    

    def last_block(self):
        return self.chain[-1]
