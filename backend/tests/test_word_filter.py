"""
Tests for word filtering functionality.
Tests removal of plurals and conjugated verbs using both SpaCy and rule-based methods.
"""

import pytest
from src.word_loader import WordLoader


class TestWordFilteringRuleBased:
    """Test word filtering with rule-based methods (fallback)."""
    
    def test_filter_plurals_rule_based(self):
        """Test plural filtering with rule-based method."""
        # Create loader with test words
        loader = WordLoader([])
        loader._words = [
            'casa',      # singular - keep
            'casas',     # plural - remove
            'livro',     # singular - keep
            'livros',    # plural - remove
            'país',      # singular ending in s - keep
            'países',    # plural - remove
            'lápis',     # singular ending in s - keep
            'ônibus',    # singular ending in s - keep
            'vírus',     # singular ending in s - keep
        ]
        
        removed = loader.filter_words(
            remove_plurals=True, 
            remove_conjugated_verbs=False,
            use_spacy=False  # Use rule-based
        )
        
        # Should remove: casas, livros, países
        assert removed == 3
        assert 'casa' in loader.words
        assert 'casas' not in loader.words
        assert 'livro' in loader.words
        assert 'livros' not in loader.words
        assert 'país' in loader.words
        assert 'países' not in loader.words
        # Should keep singular words ending in s
        assert 'lápis' in loader.words
        assert 'ônibus' in loader.words
        assert 'vírus' in loader.words
    
    def test_filter_conjugated_verbs_rule_based(self):
        """Test conjugated verb filtering with rule-based method."""
        loader = WordLoader([])
        loader._words = [
            # Infinitives - keep
            'amar',
            'comer',
            'partir',
            'por',
            
            # Conjugated forms - remove
            'amava',     # pretérito imperfeito
            'comia',     # pretérito imperfeito
            'partiu',    # pretérito perfeito (but might be kept)
            'amei',      # pretérito perfeito
            'comeram',   # pretérito perfeito
            'amando',    # gerúndio
            'comendo',   # gerúndio
            'partido',   # particípio
            'amado',     # particípio
            'comidos',   # particípio plural
            'amarei',    # futuro
            'comeria',   # futuro do pretérito
        ]
        
        removed = loader.filter_words(
            remove_plurals=False,
            remove_conjugated_verbs=True,
            use_spacy=False  # Use rule-based
        )
        
        # Should keep infinitives
        assert 'amar' in loader.words
        assert 'comer' in loader.words
        assert 'partir' in loader.words
        assert 'por' in loader.words
        
        # Should remove conjugated forms
        assert 'amava' not in loader.words
        assert 'comia' not in loader.words
        assert 'amei' not in loader.words
        assert 'comeram' not in loader.words
        assert 'amando' not in loader.words
        assert 'comendo' not in loader.words
        assert 'partido' not in loader.words
        assert 'amado' not in loader.words
        assert 'comidos' not in loader.words
        assert 'amarei' not in loader.words
        assert 'comeria' not in loader.words
        
        # At least some conjugated forms should be removed
        assert removed > 0
    
    def test_filter_both_rule_based(self):
        """Test filtering both plurals and conjugated verbs with rule-based method."""
        loader = WordLoader([])
        loader._words = [
            'casa',      # keep
            'casas',     # remove (plural)
            'amar',      # keep (infinitive)
            'amavam',    # remove (conjugated)
            'livros',    # remove (plural)
            'comendo',   # remove (gerúndio)
        ]
        
        removed = loader.filter_words(
            remove_plurals=True,
            remove_conjugated_verbs=True,
            use_spacy=False  # Use rule-based
        )
        
        # Should keep only: casa, amar
        assert len(loader.words) == 2
        assert 'casa' in loader.words
        assert 'amar' in loader.words
        assert removed == 4


class TestWordFilteringSpaCy:
    """Test word filtering with SpaCy (requires SpaCy installation)."""
    
    @pytest.fixture(autouse=True)
    def check_spacy(self):
        """Check if SpaCy is available, skip tests if not."""
        try:
            import spacy
            try:
                spacy.load("pt_core_news_sm")
            except OSError:
                pytest.skip("SpaCy Portuguese model not installed")
        except ImportError:
            pytest.skip("SpaCy not installed")
    
    def test_filter_plurals_spacy(self):
        """Test plural filtering with SpaCy."""
        loader = WordLoader([])
        loader._words = [
            'casa',      # singular - keep
            'casas',     # plural - remove
            'livro',     # singular - keep
            'livros',    # plural - remove
            'gato',      # singular - keep
            'gatos',     # plural - remove
        ]
        
        removed = loader.filter_words(
            remove_plurals=True,
            remove_conjugated_verbs=False,
            use_spacy=True
        )
        
        # Should remove plurals
        assert 'casa' in loader.words
        assert 'casas' not in loader.words
        assert 'livro' in loader.words
        assert 'livros' not in loader.words
        assert removed > 0
    
    def test_filter_conjugated_verbs_spacy(self):
        """Test conjugated verb filtering with SpaCy."""
        loader = WordLoader([])
        loader._words = [
            'amar',      # infinitive - keep
            'comer',     # infinitive - keep
            'partir',    # infinitive - keep
            'amava',     # conjugated - remove
            'comendo',   # gerund - remove
            'amado',     # participle - remove
        ]
        
        removed = loader.filter_words(
            remove_plurals=False,
            remove_conjugated_verbs=True,
            use_spacy=True
        )
        
        # Should keep infinitives
        assert 'amar' in loader.words
        assert 'comer' in loader.words
        assert 'partir' in loader.words
        
        # Should remove some conjugated forms
        assert removed > 0
    
    def test_filter_both_spacy(self):
        """Test filtering both with SpaCy."""
        loader = WordLoader([])
        loader._words = [
            'casa',      # keep
            'casas',     # remove (plural)
            'amar',      # keep (infinitive)
            'amavam',    # remove (conjugated)
            'livros',    # remove (plural)
        ]
        
        removed = loader.filter_words(
            remove_plurals=True,
            remove_conjugated_verbs=True,
            use_spacy=True
        )
        
        assert 'casa' in loader.words
        assert 'amar' in loader.words
        assert removed > 0


class TestWordFilteringGeneral:
    """Test general word filtering functionality."""
    
    def test_filter_disabled(self):
        """Test that filtering can be disabled."""
        loader = WordLoader([])
        original_words = ['casa', 'casas', 'amar', 'amava']
        loader._words = original_words.copy()
        
        removed = loader.filter_words(
            remove_plurals=False,
            remove_conjugated_verbs=False,
            use_spacy=False
        )
        
        # Nothing should be removed
        assert removed == 0
        assert len(loader.words) == len(original_words)
        for word in original_words:
            assert word in loader.words
    
    def test_filter_preserves_hyphens(self):
        """Test that words with hyphens are preserved."""
        loader = WordLoader([])
        loader._words = [
            'guarda-chuva',
            'bem-vindo',
            'guarda-chuvas',  # plural with hyphen
            'porta-aviões',
        ]
        
        removed = loader.filter_words(
            remove_plurals=True,
            remove_conjugated_verbs=True,
            use_spacy=False  # Rule-based respects hyphens
        )
        
        # Words with hyphens should be kept regardless
        assert 'guarda-chuva' in loader.words
        assert 'bem-vindo' in loader.words
        assert 'guarda-chuvas' in loader.words
        assert 'porta-aviões' in loader.words
        assert removed == 0


class TestRuleBasedHelpers:
    """Test rule-based helper methods directly."""
    
    def test_is_plural_rule_based(self):
        """Test plural detection logic."""
        loader = WordLoader([])
        
        # Plurals
        assert loader._is_plural_rule_based('casas') == True
        assert loader._is_plural_rule_based('livros') == True
        assert loader._is_plural_rule_based('palavras') == True
        
        # Singulars ending in s
        assert loader._is_plural_rule_based('país') == False
        assert loader._is_plural_rule_based('lápis') == False
        assert loader._is_plural_rule_based('ônibus') == False
        assert loader._is_plural_rule_based('vírus') == False
        
        # Non-plurals
        assert loader._is_plural_rule_based('casa') == False
        assert loader._is_plural_rule_based('livro') == False
        
        # Short words
        assert loader._is_plural_rule_based('as') == False
        assert loader._is_plural_rule_based('os') == False
    
    def test_is_conjugated_verb_rule_based(self):
        """Test conjugated verb detection logic."""
        loader = WordLoader([])
        
        # Infinitives (not conjugated)
        assert loader._is_conjugated_verb_rule_based('amar') == False
        assert loader._is_conjugated_verb_rule_based('comer') == False
        assert loader._is_conjugated_verb_rule_based('partir') == False
        assert loader._is_conjugated_verb_rule_based('por') == False
        
        # Conjugated forms
        assert loader._is_conjugated_verb_rule_based('amava') == True
        assert loader._is_conjugated_verb_rule_based('comia') == True
        assert loader._is_conjugated_verb_rule_based('amei') == True
        assert loader._is_conjugated_verb_rule_based('amando') == True
        assert loader._is_conjugated_verb_rule_based('comendo') == True
        assert loader._is_conjugated_verb_rule_based('amado') == True
        assert loader._is_conjugated_verb_rule_based('partido') == True
        
        # Short words (not flagged)
        assert loader._is_conjugated_verb_rule_based('vi') == False
        assert loader._is_conjugated_verb_rule_based('li') == False
