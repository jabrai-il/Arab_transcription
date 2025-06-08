import sys
from pathlib import Path

# Assurons-nous que le module parent est dans le chemin de recherche
parent_dir = Path(__file__).parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

from arab_transliterator.transliterator import ArabTransliterator

def print_comparison(arabic_text, transliterated_text):
    """Affiche côte à côte le texte arabe et sa translittération."""
    print(f"Arabe: {arabic_text}")
    print(f"Trans: {transliterated_text}")
    print("-" * 50)

def test_transliterator():
    """Fonction principale de test du translittérateur."""
    transliterator = ArabTransliterator()
    
    # Liste des exemples de test
    test_cases = [
        # 1. Texte arabe simple
        "السَّلَّامُ عَلَيْكُمْ",
        
        # 2. Teste le mot "الله" seul
        "اللهُ",
        
        # 3. Teste "الله" dans une phrase
        "بِسْمِ اللهِ الرَّحْمَنِ الرَّحِيمِ",
        
        # 4. Teste les symboles spéciaux
        "قَالَ النَّبِيُّ مُحَمَّدٌ ﷺ",
        
        # 5. Teste la ponctuation arabe
        "هَلْ تَعْلَمْ؟ نَعَمْ، أَعْلَمُ!",
        
        # 6. Teste les chiffres arabes et latins
        "الصَّفْحَةُ ١٢٣ - الْفَصْلُ 456",
        
        # 7. Teste une combinaison de tout
        "قَالَ اللهُ تَعَالَى: ﴿وَاللهُ يَدْعُو إِلَى دَارِ السَّلَامِ﴾ [يونس: ٢٥]",
        
        # 8. Teste la vocalisation complète
        "اَلْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        
        # 9. Teste "الله" avec des préfixes
        "وَاللهِ، بِاللَّهِ، لِلَّهِ، فَاللَّهُ",
        
        # 10. Test tanwiin
        "عَنَّا مُحَمَّدًا الْمُخْتَارَ فِي الْقِدَمِ",
        
        # 11. Expressions courantes contenant "الله"
        "الْحَمْدُ لِلَّهِ، إِنْ شَاءَ اللَّهُ، سُبْحَانَ اللَّهِ"
    ]
    
    # Tester chaque cas
    for idx, arabic_text in enumerate(test_cases, 1):
        print(f"Test #{idx}:")
        transliterated_text = transliterator.translate(arabic_text)
        print_comparison(arabic_text, transliterated_text)
    
    # Test avec un texte personnalisé (pour tests rapides pendant le développement)
    custom_text = "اللهم صل على محمد ﷺ"
    print("Test personnalisé:")
    transliterated_text = transliterator.translate(custom_text)
    print_comparison(custom_text, transliterated_text)

if __name__ == "__main__":
    print("Démarrage des tests du translittérateur arabe...")
    test_transliterator()
    print("Tests terminés!")