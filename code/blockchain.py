from time import time


class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []

    def new_block(self):
        # Creer un nouveau block dans la chaine
        pass

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
        # Hash un block
        pass

    def last_block(self):
        # Retourne le dernier block de la chaine
        pass
