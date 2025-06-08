from . import alphabet
from .mapping import _mapping
from .arab_text import ArabicText
import re


def normalize(text):
    # some text may have shadda coming after a vowel whic in this case
    # will fail the script, so were swapping
    text = list(text)
    for i, c in enumerate(text):
        if c == alphabet.SHADDA:
            if text[i - 1] in alphabet.VOWELS:
                text[i], text[i - 1] = text[i - 1], text[i]
            elif (text[i - 1] == alphabet.LAM) and not (text[i + 1] in alphabet.VOWELS):
                text.insert(i + 1, alphabet.FATHA)
    return text


class ArabTransliterator:
    def __init__(self):
        self.table = _mapping
        # Définir une liste de signes de ponctuation à préserver
        self.punctuation = [
            '،', '؟', '!', '.', ':', ';', '(', ')', '[', ']', '{', '}', '"', "'", '؛',
            ',', '?', '-', '_', '/', '\\', '«', '»', '*', '&', '%', '$', '#', '@',
            '+', '=', '<', '>', '|', '~', '^', '٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            # Symboles islamiques spéciaux
            'ﷺ', 'ﷻ', 'ﷲ', '﷽', '﴿', '﴾'
        ]
        
        # Mapping des signes de ponctuation arabes vers latins
        self.punctuation_mapping = {
            '،': ',',  # Virgule arabe vers virgule latine
            '؛': ';',  # Point-virgule arabe vers latin
            '؟': '?',  # Point d'interrogation arabe vers latin
            '﴿': '«',  # Inverser les symboles de citation coranique pour la lecture de gauche à droite
            '﴾': '»',  # Inverser les symboles de citation coranique pour la lecture de gauche à droite
        }

    def get(self, key):
        return self.table.get(key, " ")

    def translate(self, text):
        if not text:
            return ""
        
        # Ajouter les symboles spéciaux à la liste des ponctuations
        special_symbols = ['ﷺ', 'ﷻ', 'ﷲ', '﷽', '﴿', '﴾']
        for symbol in special_symbols:
            if symbol not in self.punctuation:
                self.punctuation.append(symbol)
                
        out = []
        text = normalize(text)
        arabic_text = iter(ArabicText(text))
        
        # Pour suivre si nous sommes après un tanwin
        after_tanwin = False

        for caracter in arabic_text:
            # Suivre si on est après un tanwin pour le prochain caractère
            if caracter in [alphabet.FATHATAN, alphabet.DAMMATAN, alphabet.KASRATAN]:
                after_tanwin = True
            elif not caracter.is_blank():
                # Réinitialiser si ce n'est pas un espace (car les espaces ne changent pas cet état)
                after_tanwin = False

            # Vérifier si le caractère est un signe de ponctuation
            if str(caracter) in self.punctuation:
                # Utiliser le mapping de ponctuation si disponible, sinon conserver tel quel
                out.append(self.punctuation_mapping.get(str(caracter), str(caracter)))
                continue
            
            # Vérifier si on a le début de "الله"
            if (caracter == alphabet.ALIF and 
                caracter.get_lookahead(1) == alphabet.LAM and 
                caracter.get_lookahead(2) == alphabet.LAM and 
                caracter.get_lookahead(3) == alphabet.HA):
                
                # Par défaut, utiliser "l-"
                prefix = "l-"
                
                # Cas 1: UNIQUEMENT début de phrase (pas simplement début de mot)
                # On vérifie si c'est le début absolu ou après ponctuation/nouvelle ligne
                if (not caracter.prev() or 
                    (caracter.prev().is_blank() and (not caracter.prev().prev() or 
                                                    caracter.prev().prev() in ['.', '!', '?', '،', '؟', '\n']))):
                    prefix = "al-"
                # Cas 2: Précédé par un tanwin
                elif after_tanwin or caracter.prev() in [alphabet.FATHATAN, alphabet.DAMMATAN, alphabet.KASRATAN]:
                    prefix = "il-"
                
                # Avancer jusqu'à HA et traiter les diacritiques
                next(arabic_text)  # LAM
                next(arabic_text)  # LAM
                ha = next(arabic_text)  # HA
                
                # Vérifier si HA a des diacritiques
                next_char = ha.next()
                if next_char and next_char in alphabet.VOWELS:
                    if next_char == alphabet.FATHA:
                        out.append(f"{prefix}lāha")
                        next(arabic_text)  # Consommer la voyelle
                    elif next_char == alphabet.DAMMA:
                        out.append(f"{prefix}lāhu")
                        next(arabic_text)  # Consommer la voyelle
                    elif next_char == alphabet.KASRA:
                        out.append(f"{prefix}lāhi")
                        next(arabic_text)  # Consommer la voyelle
                    else:
                        out.append(f"{prefix}lāh")
                else:
                    out.append(f"{prefix}lāh")
                
                continue
                
            # handle hamza
            if caracter in alphabet.HAMZAS:
                if caracter.is_mid():
                    out.append("'")
                continue

            # handle lam
            elif caracter == alphabet.LAM:
                sun = caracter.is_sun()
                
                # handle alif lam (article défini)
                if (p := caracter.prev()) == alphabet.ALIF:
                    # Déterminer le préfixe en fonction du contexte
                    prefix = ""
                    possible_tanwin_other = p.prev().prev() if p.prev() else None
                    possible_tanwin_fatha = p.prev().prev().prev() if p.prev() and p.prev().prev() else None
                    
                    # Cas 1: UNIQUEMENT début de phrase (pas simplement début de mot)
                    if (not p.prev() or 
                        (p.prev().is_blank() and (not p.prev().prev() or 
                                                 p.prev().prev() in ['.', '!', '?', '،', '؟', '\n']))):
                        if sun:
                            prefix = "a"  # Pour les lettres solaires: as-shams
                        else:
                            prefix = "al-"  # Pour les lettres lunaires: al-qamar
                    
                    # Cas 2: Précédé par un tanwin
                    
                    elif (possible_tanwin_fatha and possible_tanwin_fatha in [alphabet.FATHATAN, alphabet.DAMMATAN, alphabet.KASRATAN]) or (possible_tanwin_other and possible_tanwin_other in [alphabet.FATHATAN, alphabet.DAMMATAN, alphabet.KASRATAN]):
                        if sun:
                            prefix = "i"  # Pour les lettres solaires après tanwin
                        else:
                            prefix = "il-"  # Pour les lettres lunaires après tanwin
                    
                    # Cas 3: Autres cas (milieu de phrase)
                    else:
                        if sun:
                            prefix = ""  # Pas de préfixe pour les lettres solaires: s-shams
                        else:
                            prefix = "l-"  # Pour les lettres lunaires: l-qamar
                    
                    out.append(prefix)
                    
                # handle alif with hamzat wasl
                elif (p := caracter.prev()) == alphabet.ALIF_WITH_HAMZAT_WASL:
                    out[-1] = "a" if p.is_start() else "l-"
                
                # Autres cas pour lam
                else:
                    out.append("" if sun else "l")

                # Traitement des lettres solaires
                if sun:
                    sep = "-" if caracter.prev().is_word_start() else ""
                    out.append(sep.join([self.get(sun)] * 2))
                    next(arabic_text)
                    next(arabic_text)

                continue

            # handle alif
            elif caracter == alphabet.ALIF:
                if caracter.prev() == alphabet.FATHA:
                    out[-1] = "ā"
                continue

            # handle alif with hamzat wasl
            elif caracter == alphabet.ALIF_WITH_HAMZAT_WASL:
                out.append("i")
                continue

            # handle alif maksura
            elif caracter == alphabet.ALIF_MAKSURA:
                if caracter.prev() == alphabet.FATHA:
                    out[-1] = "ā"
                continue

            # handle alif with maddah above
            elif caracter == alphabet.ALIF_WITH_MADDA_ABOVE:
                out.append("ā" if caracter.is_start() else "'ā")
                continue

            # kasra + ya
            elif caracter.is_kasra_followed_by_ya():
                # Vérifier si ya est suivi d'un shadda
                if caracter.next() == alphabet.YA and caracter.next().next() == alphabet.SHADDA:
                    # Cas spécial: kasra + ya + shadda → "iyy"
                    out.append("iyy")
                    next(arabic_text)  # Consommer le ya
                    next(arabic_text)  # Consommer le shadda
                    # Si après le shadda il y a un damma ou fatha, l'ajouter
                    next_char = caracter.next(3) if caracter.next(2) else None
                    if next_char == alphabet.DAMMA:
                        out.append("u")
                        next(arabic_text)  # Consommer le damma
                    elif next_char == alphabet.FATHA:
                        out.append("a")
                        next(arabic_text)  # Consommer le fatha
                elif caracter.next(2) not in alphabet.VOWELS:
                    # Cas standard: kasra + ya → "ī"
                    out.append("ī")
                    next(arabic_text)
                else:
                    out.append("i")
                continue

            # damma + waw
            elif caracter.is_damma_followed_by_waw():
                # Vérifier si waw est suivi d'un shadda
                if caracter.next() == alphabet.WAW and caracter.next().next() == alphabet.SHADDA:
                    # Cas spécial: damma + waw + shadda → "uww"
                    out.append("uww")
                    next(arabic_text)  # Consommer le waw
                    next(arabic_text)  # Consommer le shadda
                    # Si après le shadda il y a une voyelle, l'ajouter
                    next_char = caracter.next(3) if caracter.next(2) else None
                    if next_char == alphabet.DAMMA:
                        out.append("u")
                        next(arabic_text)  # Consommer le damma
                    elif next_char == alphabet.FATHA:
                        out.append("a")
                        next(arabic_text)  # Consommer le fatha
                    elif next_char == alphabet.KASRA:
                        out.append("i")
                        next(arabic_text)  # Consommer le kasra
                elif caracter.next(2) not in alphabet.VOWELS:
                    out.append("ū")
                    next(arabic_text)
                else:
                    out.append("u")
                continue

            # handle SHADDA
            elif caracter == alphabet.SHADDA:
                vow = caracter.prev(2)
                # if preceded by YA
                if caracter.prev() == alphabet.YA:
                    if vow == alphabet.KASRA and caracter.is_mid():
                        out.append("y")

                    elif vow == alphabet.FATHA:
                        out.append("y")

                # if preceded by WAW
                elif caracter.prev() == alphabet.WAW:
                    if vow == alphabet.DAMMA:
                        out.append("w")

                    elif vow == alphabet.FATHA:
                        out.append("w")

                elif caracter.prev().is_mid():
                    if len(out) >= 2 and (not out[-2] == "l-"):
                        out.append(self.get(str(caracter.prev())))

            # handle the rest
            else:
                out.append(self.get(str(caracter)))
                if caracter.next() in (
                    alphabet.SUKUN,
                    alphabet.SMALL_HIGH_ROUNDED_ZERO,
                ):
                    if (
                        caracter.prev() == alphabet.ALIF
                        and caracter.prev().is_word_start()
                    ):
                        out[-1] = self.get(str(caracter)) + "-"

        # Obtenir le résultat initial
        result = "".join(out)
        
        # Post-traitement pour corriger certains problèmes spécifiques
        
        # 1. Assurer que "lah" est toujours écrit avec le macron: "lāh"
        result = re.sub(r'l-lah[aui]?', lambda m: m.group(0).replace('lah', 'lāh'), result)
        result = re.sub(r'al-lah[aui]?', lambda m: m.group(0).replace('lah', 'lāh'), result)
        result = re.sub(r'il-lah[aui]?', lambda m: m.group(0).replace('lah', 'lāh'), result)
        
        # 2. Corriger "wa l-" qui peut être écrit "wal-" par erreur
        result = re.sub(r'wa([a-z])-', r'wa \1-', result)
        
        # 3. Corriger les tirets mal placés
        result = re.sub(r'([a-z])-([aeiou])', r'\1\2', result)
        
        # 4. Assurer que la forme "li + l-lāh" est correctement écrite "lillāh"
        result = re.sub(r'li l-lāh([aui]?)', r'lillāh\1', result)
        
        # 5. Corriger les prépositions fusionnées avec Allah (bi, li, fa, wa)
        result = re.sub(r'billah([aui]?)', r'billāh\1', result)
        result = re.sub(r'lillah([aui]?)', r'lillāh\1', result)
        result = re.sub(r'fallah([aui]?)', r'fallāh\1', result)
        result = re.sub(r'fāllah([aui]?)', r'fallāh\1', result)
        result = re.sub(r'wallah([aui]?)', r'wallāh\1', result)
        result = re.sub(r'wāllah([aui]?)', r'wallāh\1', result)
        
        # Post-traitement pour le mot "Allah"
        # 1. Début de phrase uniquement (après ponctuation ou début absolu)
        result = re.sub(r'(^|\.\s|\!\s|\?\s|،\s|؟\s|\n\s*)l-lāh([aui]?)', r'\1al-lāh\2', result)
        
        # 2. Après tanwin (utiliser le symbole de tanwin adéquat selon votre système)
        result = re.sub(r'([ⁿᵐⁱ])l-lāh([aui]?)', r'\1il-lāh\2', result)
        
        # 3. Pour les occurrences intermédiaires, garder "l-lāh"
        # (pas besoin de règle supplémentaire)
        
        # Normaliser les espaces
        result = " ".join(filter(None, result.split(" ")))
        
        return result


if __name__ == "__main__":
    from pathlib import Path
    import argparse

    translator = ArabTransliterator()

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="The arab file you want the transcription")
    parser.add_argument("-t", "--text", help="The arab text you want the transcription")
    args = parser.parse_args()

    if args.file:
        file = Path(args.file)
        lines = file.read_bytes().decode("utf-8").split("\n")
        print(*map(translator.translate, lines), sep="\n")

    elif args.text:
        print(translator.translate(args.text))
