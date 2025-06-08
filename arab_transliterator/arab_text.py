from . import alphabet
from ._types import LinkedQueue


class ArabicText(LinkedQueue):
    class ArabicTextChar:
        def __init__(self, parent, node):
            self._node = node
            self._parent = parent
            # Ajouter un attribut index pour faciliter le lookahead
            self.index = parent._find_index(node)

        def char(self):
            return self._node._ele

        def __eq__(self, other):
            return self.char() == other

        def __str__(self):
            return self.char()

        def next(self, val=None):
            if not val:
                return self._parent.after(self)
            ele = self
            while val != 0 and ele.next():
                ele = ele.next()
                val -= 1
            return ele

        def prev(self, val=None):
            if not val:
                return self._parent.before(self)
            ele = self
            while val != 0 and ele.prev():
                ele = ele.prev()
                val -= 1
            return ele
            
        def get_lookahead(self, offset=1):
            """Retourne le caractère à la position offset sans avancer le curseur"""
            if offset <= 0:
                return self.char()
            
            # Utiliser la méthode next() pour obtenir le caractère à la position offset
            lookahead = self
            for _ in range(offset):
                lookahead = lookahead.next()
                if lookahead is None:
                    return None
            
            return lookahead.char()

        def is_blank(self):
            return self == " "

        def is_start(self):
            return self._node is self._parent._head

        def is_mid(self):
            try:
                return (not self.is_word_start()) and (not self.next().is_blank())
            except Exception:
                return False

        def is_end(self):
            return self._node is self._parent._tail

        def is_word_start(self):
            return self.prev() == " " or (not self.prev())

        def is_phrase_start(self):
            return (not self.prev()) or (not self.prev().prev()) or self.prev().prev() == " "
        
        
        def preceeded(self, n):
            out = ""
            ele = self
            while n != 0 and ele.prev():
                out += ele.prev().char()
                ele = ele.prev()
                n -= 1
            return out

        def succeeded(self, n):
            out = ""
            ele = self
            while n != 0 and ele.next():
                out += ele.next().char()
                ele = ele.next()
                n -= 1
            return out

        def is_sun(self):
            c = self.next()
            if not c:
                return False
            if c.is_followed_by_shadda():
                return self.next().char()
            return False

        def is_followed_by_sun(self):
            lam_node = self.next()
            if lam_node.next().is_followed_by_shadda():
                return lam_node.next().char()
            return False

        def is_followed_by_shadda(self):
            return self.next() == alphabet.SHADDA

        def is_fatha_followed_by_alif(self):
            try:
                return self == alphabet.FATHA and self.next().is_alif()
            except Exception:
                return False

        def is_kasra_followed_by_ya(self):
            return self == alphabet.KASRA and self.next() == alphabet.YA

        def is_damma_followed_by_waw(self):
            return self == alphabet.DAMMA and self.next() == alphabet.WAW

    def __init__(self, text):
        super().__init__()
        for c in text:
            self.enqueue(c)
        self.cursor = None
        self._state_stack = []  # Pour sauvegarder et restaurer l'état

    def _find_index(self, node):
        """Trouve l'index d'un nœud dans la file"""
        if node is None:
            return -1
        
        current = self._head
        index = 0
        while current is not None:
            if current == node:
                return index
            current = current._next
            index += 1
        return -1

    def _make_position(self, node):
        if node is None:
            return None
        return self.ArabicTextChar(self, node)

    def first(self):
        return self._make_position(self._head)

    def after(self, p):
        return self._make_position(p._node._next)

    def before(self, p):
        return self._make_position(p._node._prev)

    def get_state(self):
        """Retourne l'état actuel de l'itérateur"""
        if self.cursor is None:
            return None
        return self.cursor._node

    def set_state(self, state):
        """Restaure l'état de l'itérateur"""
        if state is None:
            self.cursor = None
        else:
            self.cursor = self._make_position(state)
        return self.cursor

    def __iter__(self):
        cursor = self.first()
        while cursor is not None:
            self.cursor = cursor
            yield cursor
            cursor = self.after(cursor)
