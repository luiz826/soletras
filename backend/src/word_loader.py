"""
Word list loader module.
Handles loading and caching of word lists from various sources.
"""

import urllib.request
import os
import pickle
import hashlib
from pathlib import Path
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)

# SpaCy imports - lazy loading
_nlp = None


def get_nlp():
    """
    Lazy load SpaCy model.
    Downloads the model if not available.
    """
    global _nlp
    if _nlp is None:
        try:
            import spacy
            try:
                _nlp = spacy.load("pt_core_news_sm")
                logger.info("SpaCy Portuguese model loaded successfully")
            except OSError:
                logger.warning("SpaCy Portuguese model not found. Downloading...")
                import subprocess
                subprocess.run(
                    ["python", "-m", "spacy", "download", "pt_core_news_sm"],
                    check=True,
                    capture_output=True
                )
                _nlp = spacy.load("pt_core_news_sm")
                logger.info("SpaCy Portuguese model downloaded and loaded")
        except ImportError:
            logger.error("SpaCy not installed. Install with: pip install spacy")
            raise ImportError(
                "SpaCy is required for word filtering. "
                "Install with: pip install spacy && python -m spacy download pt_core_news_sm"
            )
    return _nlp


class WordLoader:
    """Handles loading words from single or multiple URL/file sources."""
    
    # Cache directory for filtered words and source words
    CACHE_DIR = Path('data/cache')
    SOURCE_CACHE_FILE = CACHE_DIR / 'source_words.pkl'
    
    # Preprocessed directory for pre-computed filtered words (no SpaCy needed)
    PREPROCESSED_DIR = Path('data/preprocessed')
    
    def __init__(self, sources: Union[str, List[str]]):
        """
        Initialize the word loader.
        
        Args:
            sources: Single source (string) or list of sources (URLs or file paths)
        """
        # Convert single source to list for uniform handling
        if isinstance(sources, str):
            self.sources = [sources]
        else:
            self.sources = sources
        
        self._words: List[str] = []
        self._source_stats: dict = {}  # Track stats per source
        
        # Ensure cache directory exists
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    @property
    def source(self) -> str:
        """Get the first source (for backward compatibility)."""
        return self.sources[0] if self.sources else ""
    
    @property
    def words(self) -> List[str]:
        """Get the loaded words."""
        return self._words
    
    @property
    def word_count(self) -> int:
        """Get the number of loaded words."""
        return len(self._words)
    
    @property
    def source_stats(self) -> dict:
        """Get statistics per source."""
        return self._source_stats
    
    def _get_sources_cache_key(self) -> str:
        """
        Generate cache key based on sources list.
        
        Returns:
            Hash string for cache validation
        """
        # Create a stable hash of sources
        sources_str = '|'.join(sorted(self.sources))
        return hashlib.md5(sources_str.encode()).hexdigest()
    
    def _load_from_source_cache(self) -> Optional[List[str]]:
        """
        Load words from source cache (cached downloaded words).
        
        Returns:
            List of cached words, or None if cache miss/invalid
        """
        if not self.SOURCE_CACHE_FILE.exists():
            logger.debug("Source cache file not found")
            return None
        
        try:
            logger.info(f"Checking source cache: {self.SOURCE_CACHE_FILE.name}")
            with open(self.SOURCE_CACHE_FILE, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Validate cache
            if not isinstance(cached_data, dict):
                logger.warning("Invalid source cache format")
                return None
            
            # Check if sources match
            cached_key = cached_data.get('sources_key')
            current_key = self._get_sources_cache_key()
            
            if cached_key != current_key:
                logger.info("Source list changed, cache invalidated")
                return None
            
            words = cached_data.get('words')
            stats = cached_data.get('source_stats', {})
            timestamp = cached_data.get('timestamp', 'unknown')
            
            if words and isinstance(words, list):
                self._source_stats = stats
                logger.info(f"✅ Loaded {len(words)} words from source cache (saved at {timestamp})")
                return words
            
            logger.warning("Invalid cache data")
            return None
            
        except Exception as e:
            logger.warning(f"Failed to load source cache: {e}")
            return None
    
    def _save_to_source_cache(self, words: List[str]) -> None:
        """
        Save downloaded words to source cache.
        
        Args:
            words: Word list to cache
        """
        try:
            from datetime import datetime
            
            cache_data = {
                'words': words,
                'sources_key': self._get_sources_cache_key(),
                'sources': self.sources,
                'source_stats': self._source_stats,
                'timestamp': datetime.now().isoformat(),
                'word_count': len(words)
            }
            
            logger.info(f"Saving {len(words)} words to source cache: {self.SOURCE_CACHE_FILE.name}")
            with open(self.SOURCE_CACHE_FILE, 'wb') as f:
                pickle.dump(cache_data, f)
            
            file_size = self.SOURCE_CACHE_FILE.stat().st_size / 1024
            logger.info(f"✅ Source cache saved successfully ({file_size:.1f} KB)")
            
        except Exception as e:
            logger.error(f"Failed to save source cache: {e}")
    
    def load(self) -> None:
        """
        Load words from all configured sources and merge them.
        Uses preprocessed or cache files to avoid re-downloading if available.
        
        Raises:
            Exception: If all sources fail to load
        """
        # Priority 1: Try to load from preprocessed source words (production deployment)
        preprocessed_source_file = self.PREPROCESSED_DIR / 'source_words.pkl'
        
        if preprocessed_source_file.exists():
            try:
                logger.info(f"Loading from preprocessed source file: {preprocessed_source_file.name}")
                with open(preprocessed_source_file, 'rb') as f:
                    self._words = pickle.load(f)
                
                logger.info(
                    f"✅ Loaded {len(self._words)} words from preprocessed file (no download needed!)"
                )
                return
            except Exception as e:
                logger.warning(f"Failed to load preprocessed source file: {e}, trying cache...")
        
        # Priority 2: Try to load from source cache
        cached_words = self._load_from_source_cache()
        
        if cached_words is not None:
            # Cache hit - use cached words
            self._words = cached_words
            logger.info(
                f"✅ Using source cache - {len(self._words)} words loaded instantly! "
                f"(from {len(self.sources)} source(s))"
            )
            return
        
        # Priority 3: No preprocessed file or cache - need to download from sources
        logger.info("⚙️ No preprocessed file or cache - downloading from sources...")
        
        all_words = set()  # Use set to automatically deduplicate
        successful_loads = 0
        failed_sources = []
        
        logger.info(f"Loading words from {len(self.sources)} source(s)...")
        
        for source in self.sources:
            try:
                words = self._load_single_source(source)
                initial_count = len(words)
                
                # Add to set (deduplicates automatically)
                all_words.update(words)
                
                # Track stats
                self._source_stats[source] = {
                    'words_loaded': initial_count,
                    'status': 'success'
                }
                
                successful_loads += 1
                logger.info(f"✓ Loaded {initial_count} words from: {self._truncate_source(source)}")
            
            except Exception as e:
                logger.warning(f"✗ Failed to load from {self._truncate_source(source)}: {e}")
                self._source_stats[source] = {
                    'words_loaded': 0,
                    'status': 'failed',
                    'error': str(e)
                }
                failed_sources.append(source)
        
        if successful_loads == 0:
            error_msg = f"Failed to load from all {len(self.sources)} source(s)"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Convert set to sorted list
        self._words = sorted(list(all_words))
        
        # Save to source cache for next time
        self._save_to_source_cache(self._words)
        
        logger.info(
            f"Successfully loaded {self.word_count} unique words from "
            f"{successful_loads}/{len(self.sources)} source(s)"
        )
        
        if failed_sources:
            logger.warning(f"Failed sources: {len(failed_sources)}/{len(self.sources)}")
    
    def _truncate_source(self, source: str, max_length: int = 60) -> str:
        """Truncate source string for logging."""
        if len(source) <= max_length:
            return source
        return source[:max_length] + "..."
    
    def _load_single_source(self, source: str) -> List[str]:
        """
        Load words from a single source.
        
        Args:
            source: URL or file path
        
        Returns:
            List of words from this source
        
        Raises:
            Exception: If loading fails
        """
        if self._is_url(source):
            return self._load_from_url(source)
        else:
            return self._load_from_file(source)
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        return source.startswith('http://') or source.startswith('https://')
    
    def _load_from_url(self, url: str) -> List[str]:
        """
        Load words from a URL.
        
        Args:
            url: URL to load from
        
        Returns:
            List of words
        """
        with urllib.request.urlopen(url, timeout=30) as response:
            # Try different encodings for .dic files
            if url.endswith('.dic'):
                try:
                    content = response.read().decode('latin-1')
                except:
                    content = response.read().decode('utf-8', errors='ignore')
            else:
                content = response.read().decode('utf-8', errors='ignore')
            
            # Use special parsing for .dic files
            if url.endswith('.dic'):
                return self._parse_dic_content(content)
            else:
                return self._parse_content(content)
    
    def _load_from_file(self, filepath: str) -> List[str]:
        """
        Load words from a local file.
        
        Args:
            filepath: Path to file
        
        Returns:
            List of words
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Word file not found: {filepath}")
        
        # Use special parsing for .dic files
        if filepath.endswith('.dic'):
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            return self._parse_dic_content(content)
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return self._parse_content(content)
    
    def _parse_content(self, content: str) -> List[str]:
        """
        Parse content and extract words.
        
        Special handling for different file formats:
        - .dic files (LibreOffice): Skip first line (word count) and remove suffix markers
        - Plain text: One word per line
        
        Args:
            content: Raw text content
        
        Returns:
            List of cleaned, normalized words
        """
        words = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip first line if it looks like a count (common in .dic files)
            if i == 0 and line.isdigit():
                continue
            
            # Remove suffix markers from .dic files (e.g., "palavra/123")
            if '/' in line:
                line = line.split('/')[0].strip()
            
            # Convert to lowercase and filter out non-alphabetic entries
            word = line.lower()
            
            # Only include if it contains at least some alphabetic characters
            if word and any(c.isalpha() for c in word):
                # Remove non-alphabetic characters except hyphens
                word = ''.join(c for c in word if c.isalpha() or c == '-')
                if word:
                    words.append(word)
        
        return words
    
    def _parse_dic_content(self, content: str) -> List[str]:
        """
        Parse LibreOffice .dic file content.
        
        Special handling for .dic files:
        - Skip first line (word count)
        - Remove suffix markers (e.g., "palavra/123")
        - Split compound words with hyphens
        - Skip city names (words ending with uppercase 2-letter codes like -SP, -RJ)
        
        Args:
            content: Raw text content from .dic file
        
        Returns:
            List of cleaned, normalized words
        """
        palavras = set()
        lines = content.split('\n')
        
        for i, linha in enumerate(lines):
            # Skip first line (word count)
            if i == 0:
                continue
            
            linha = linha.strip()
            
            # Skip empty lines
            if not linha:
                continue
            
            # Remove suffix markers (e.g., "palavra/123")
            if '/' in linha:
                linha = linha.split('/')[0].strip()
            
            # Split compound words by hyphen
            partes = linha.split('-')
            sufixo = partes[-1]
            
            # Skip city names (words ending with uppercase 2-letter codes like -SP, -RJ)
            if len(sufixo) == 2 and sufixo.upper() == sufixo:
                continue
            
            # Convert to lowercase
            palavra = linha.lower()
            
            # Add full compound word if valid
            if palavra and any(c.isalpha() for c in palavra):
                # Remove non-alphabetic characters except hyphens
                palavra_limpa = ''.join(c for c in palavra if c.isalpha() or c == '-')
                if palavra_limpa:
                    palavras.add(palavra_limpa)
            
            # Add individual parts of compound words
            if len(partes) > 1:
                for parte in partes:
                    parte = parte.lower().strip()
                    if parte and any(c.isalpha() for c in parte):
                        # Remove non-alphabetic characters
                        parte_limpa = ''.join(c for c in parte if c.isalpha())
                        if parte_limpa:
                            palavras.add(parte_limpa)
        
        logger.debug(f"Parsed .dic file: {len(palavras)} unique words")
        return sorted(list(palavras))
    
    def _get_cache_key(self, remove_plurals: bool, remove_conjugated_verbs: bool) -> str:
        """
        Generate cache key based on filter settings and word count.
        
        Args:
            remove_plurals: Whether plurals are removed
            remove_conjugated_verbs: Whether conjugated verbs are removed
        
        Returns:
            Hash string for cache filename
        """
        # Include word count to invalidate cache when word list changes
        word_count = len(self._words)
        key = f"words_{self._words}_pl_{remove_plurals}_vb_{remove_conjugated_verbs}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_filepath(self, remove_plurals: bool, remove_conjugated_verbs: bool) -> Path:
        """Get cache file path for given filter settings."""
        cache_key = self._get_cache_key(remove_plurals, remove_conjugated_verbs)
        return self.CACHE_DIR / f"filtered_{cache_key}.pkl"
    
    def _get_preprocessed_filepath(self, remove_plurals: bool, remove_conjugated_verbs: bool) -> Path:
        """Get preprocessed file path for given filter settings."""
        filename = f"words_p{int(remove_plurals)}_v{int(remove_conjugated_verbs)}.pkl"
        return self.PREPROCESSED_DIR / filename
    
    def _load_from_preprocessed(self, remove_plurals: bool, remove_conjugated_verbs: bool) -> Optional[List[str]]:
        """
        Load filtered words from preprocessed files (no SpaCy needed).
        These files are generated locally and committed to the repo.
        
        Args:
            remove_plurals: Plural filter setting
            remove_conjugated_verbs: Verb filter setting
        
        Returns:
            List of preprocessed filtered words, or None if file not found
        """
        preprocessed_file = self._get_preprocessed_filepath(remove_plurals, remove_conjugated_verbs)
        
        if preprocessed_file.exists():
            try:
                logger.info(f"Loading from preprocessed file: {preprocessed_file.name}")
                with open(preprocessed_file, 'rb') as f:
                    words = pickle.load(f)
                
                logger.info(f"✅ Loaded {len(words)} preprocessed words (no SpaCy needed!)")
                return words
            except Exception as e:
                logger.warning(f"Failed to load preprocessed file: {e}")
                return None
        
        logger.debug(f"Preprocessed file not found: {preprocessed_file.name}")
        return None
    
    def _load_from_disk_cache(self, remove_plurals: bool, remove_conjugated_verbs: bool) -> Optional[List[str]]:
        """
        Load filtered words from disk cache.
        
        Args:
            remove_plurals: Plural filter setting
            remove_conjugated_verbs: Verb filter setting
        
        Returns:
            List of cached filtered words, or None if cache miss
        """
        cache_file = self._get_cache_filepath(remove_plurals, remove_conjugated_verbs)
        
        if cache_file.exists():
            try:
                logger.info(f"Loading from disk cache: {cache_file.name}")
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    
                # Validate cache data
                if isinstance(cached_data, dict) and 'words' in cached_data:
                    words = cached_data['words']
                    logger.info(f"✅ Loaded {len(words)} words from disk cache (saved at {cached_data.get('timestamp', 'unknown')})")
                    return words
                elif isinstance(cached_data, list):
                    # Legacy format
                    logger.info(f"✅ Loaded {len(cached_data)} words from disk cache")
                    return cached_data
                else:
                    logger.warning("Invalid cache format, will regenerate")
                    return None
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}, will regenerate")
                return None
        
        logger.debug("Cache miss - file not found")
        return None
    
    def _save_to_disk_cache(
        self,
        remove_plurals: bool,
        remove_conjugated_verbs: bool,
        words: List[str]
    ) -> None:
        """
        Save filtered words to disk cache.
        
        Args:
            remove_plurals: Plural filter setting
            remove_conjugated_verbs: Verb filter setting
            words: Filtered word list to cache
        """
        cache_file = self._get_cache_filepath(remove_plurals, remove_conjugated_verbs)
        
        try:
            from datetime import datetime
            
            cache_data = {
                'words': words,
                'timestamp': datetime.now().isoformat(),
                'word_count': len(words),
                'filters': {
                    'remove_plurals': remove_plurals,
                    'remove_conjugated_verbs': remove_conjugated_verbs
                }
            }
            
            logger.info(f"Saving {len(words)} words to disk cache: {cache_file.name}")
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info(f"✅ Cache saved successfully ({cache_file.stat().st_size / 1024:.1f} KB)")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def filter_words(
        self,
        remove_plurals: bool = True,
        remove_conjugated_verbs: bool = True,
        use_spacy: bool = True
    ) -> int:
        """
        Filter words based on specified criteria using SpaCy for linguistic analysis.
        Uses disk cache to avoid reprocessing.
        
        Args:
            remove_plurals: Remove words that are in plural form
            remove_conjugated_verbs: Remove verbs not in infinitive form
            use_spacy: Use SpaCy for linguistic analysis (recommended)
        
        Returns:
            Number of words removed
        """
        if not remove_plurals and not remove_conjugated_verbs:
            logger.info("No filters enabled, skipping word filtering")
            return 0
        
        original_count = len(self._words)
        
        # Priority 1: Try to load from preprocessed files (fastest, no SpaCy needed)
        preprocessed_words = self._load_from_preprocessed(remove_plurals, remove_conjugated_verbs)
        
        if preprocessed_words is not None:
            # Preprocessed file found! No SpaCy processing needed
            self._words = preprocessed_words
            removed = original_count - len(self._words)
            logger.info(
                f"✅ Used preprocessed file - {removed} words filtered. "
                f"{len(self._words)} words remaining. (No SpaCy needed!)"
            )
            return removed
        
        # Priority 2: Try to load from disk cache
        cached_words = self._load_from_disk_cache(remove_plurals, remove_conjugated_verbs)
        
        if cached_words is not None:
            # Cache hit!
            self._words = cached_words
            removed = original_count - len(self._words)
            logger.info(
                f"✅ Used disk cache - {removed} words filtered. "
                f"{len(self._words)} words remaining."
            )
            return removed
        
        # Priority 3: No preprocessed file or cache - need to process with SpaCy
        logger.info("⚙️ No preprocessed file or cache - processing words with filters...")
        
        if use_spacy:
            filtered_words = self._filter_with_spacy(remove_plurals, remove_conjugated_verbs)
        else:
            # Fallback to rule-based filtering
            filtered_words = []
            for word in self._words:
                if self._should_keep_word_rule_based(word, remove_plurals, remove_conjugated_verbs):
                    filtered_words.append(word)
        
        # Save to disk cache for next time
        self._save_to_disk_cache(remove_plurals, remove_conjugated_verbs, filtered_words)
        
        self._words = filtered_words
        removed = original_count - len(self._words)
        
        method = "SpaCy" if use_spacy else "rule-based"
        logger.info(
            f"Filtered {removed} words using {method} analysis "
            f"(plurals={remove_plurals}, conjugated_verbs={remove_conjugated_verbs}). "
            f"{len(self._words)} words remaining."
        )
        
        return removed
    
    def _filter_with_spacy(
        self,
        remove_plurals: bool,
        remove_conjugated_verbs: bool
    ) -> List[str]:
        """
        Filter words using SpaCy linguistic analysis.
        
        Args:
            remove_plurals: Remove plural words
            remove_conjugated_verbs: Remove conjugated verbs
        
        Returns:
            List of filtered words
        """
        nlp = get_nlp()
        filtered_words = []
        
        # Process words in batches for efficiency
        batch_size = 5000  # Increased from 1000 for better performance
        total_words = len(self._words)
        
        logger.info(f"Processing {total_words} words with SpaCy (batch size: {batch_size})...")
        
        for i in range(0, total_words, batch_size):
            batch = self._words[i:i + batch_size]
            
            # Process batch with SpaCy
            docs = list(nlp.pipe(batch, disable=["parser", "ner"]))
            
            for word, doc in zip(batch, docs):
                if self._should_keep_word_spacy(doc, remove_plurals, remove_conjugated_verbs):
                    filtered_words.append(word)
            
            # Log progress
            if (i + batch_size) % 5000 == 0 or (i + batch_size) >= total_words:
                processed = min(i + batch_size, total_words)
                logger.debug(f"Processed {processed}/{total_words} words...")
        
        return filtered_words
    
    def _should_keep_word_spacy(
        self,
        doc,
        remove_plurals: bool,
        remove_conjugated_verbs: bool
    ) -> bool:
        """
        Determine if a word should be kept using SpaCy analysis.
        
        Args:
            doc: SpaCy Doc object
            remove_plurals: Whether to filter out plurals
            remove_conjugated_verbs: Whether to filter out conjugated verbs
        
        Returns:
            True if word should be kept
        """
        if len(doc) == 0:
            return True
        
        # Get the first token (should be the only one for single words)
        token = doc[0]
        
        # Always keep words with hyphens or very short words
        if '-' in token.text or len(token.text) <= 2:
            return True
        
        # Check for plurals
        if remove_plurals:
            # Check if token is a noun in plural
            if token.pos_ == "NOUN" and token.morph.get("Number") == ["Plur"]:
                return False
            
            # Also check adjectives, pronouns, and determiners
            if token.pos_ in ["ADJ", "PRON", "DET"] and token.morph.get("Number") == ["Plur"]:
                return False
        
        # Check for conjugated verbs
        if remove_conjugated_verbs:
            if token.pos_ == "VERB":
                # Keep only infinitive verbs
                verb_form = token.morph.get("VerbForm")
                
                # Keep infinitives
                if verb_form == ["Inf"]:
                    return True
                
                # Remove finite verbs (conjugated)
                if verb_form == ["Fin"]:
                    return False
                
                # Remove participles and gerunds
                if verb_form in [["Part"], ["Ger"]]:
                    return False
                
                # If no verb form specified but it's tagged as VERB, be conservative
                # Check if it ends with infinitive endings
                if token.text.endswith(('ar', 'er', 'ir', 'or', 'ôr')):
                    return True
                
                # Otherwise, likely conjugated
                return False
        
        return True
    
    def _should_keep_word_rule_based(
        self,
        word: str,
        remove_plurals: bool,
        remove_conjugated_verbs: bool
    ) -> bool:
        """
        Determine if a word should be kept based on rule-based filters (fallback).
        
        Args:
            word: Word to check
            remove_plurals: Whether to filter out plurals
            remove_conjugated_verbs: Whether to filter out conjugated verbs
        
        Returns:
            True if word should be kept, False otherwise
        """
        # Don't filter very short words or words with hyphens
        if len(word) <= 2 or '-' in word:
            return True
        
        # Check for plurals (ends with -s)
        if remove_plurals and self._is_plural_rule_based(word):
            return False
        
        # Check for conjugated verbs (not in infinitive)
        if remove_conjugated_verbs and self._is_conjugated_verb_rule_based(word):
            return False
        
        return True
    
    def _is_plural_rule_based(self, word: str) -> bool:
        """
        Check if a word appears to be a plural using rule-based heuristics.
        
        Common patterns:
        - Ends in -s (but not -ês, -ás, -ós, -us when singular)
        - Exceptions: palavras que terminam naturalmente em -s no singular
        
        Args:
            word: Word to check
        
        Returns:
            True if likely a plural
        """
        if not word.endswith('s'):
            return False
        
        # Common singular words ending in -s (not plurals)
        singular_endings_s = [
            'ês', 'ás', 'ós', 'is',  # país, atrás, após, lápis
            'us',  # vírus, ônibus
            'aos', 'ões'  # mãos (plural de mão, but keep)
        ]
        
        # Exception: palavras de 3 letras ou menos geralmente não são plurais
        if len(word) <= 3:
            return False
        
        # Se termina em padrões que são naturalmente singulares, manter
        for ending in singular_endings_s:
            if word.endswith(ending) and len(word) > len(ending):
                return False
        
        # Likely a plural if ends in -s and has more than 3 letters
        return True
    
    def _is_conjugated_verb_rule_based(self, word: str) -> bool:
        """
        Check if a word is a conjugated verb using rule-based heuristics (not in infinitive form).
        
        Infinitive verbs in Portuguese end in: -ar, -er, -ir, -or, -ôr
        Conjugated verbs often end in: -ava, -ia, -ei, -ou, -am, -em, etc.
        
        This function identifies likely conjugated forms to remove them.
        
        Args:
            word: Word to check
        
        Returns:
            True if likely a conjugated verb (should be removed)
        """
        if len(word) <= 3:
            return False
        
        # Infinitive endings (keep these)
        infinitive_endings = ['ar', 'er', 'ir', 'or', 'ôr']
        
        # Check if word ends with infinitive - if yes, it's NOT conjugated
        for ending in infinitive_endings:
            if word.endswith(ending):
                return False
        
        # Common conjugated verb endings (remove these)
        conjugated_endings = [
            'ava', 'avam', 'ávamos',  # pretérito imperfeito -ar
            'ia', 'iam', 'íamos',      # pretérito imperfeito -er/-ir
            'ei', 'ou', 'aste', 'aram',  # pretérito perfeito
            'eria', 'eriam', 'eríamos',  # futuro do pretérito
            'arei', 'arão', 'aremos',    # futuro do presente -ar
            'erei', 'erão', 'eremos',    # futuro do presente -er
            'irei', 'irão', 'iremos',    # futuro do presente -ir
            'ando', 'endo', 'indo',      # gerúndio
            'ado', 'ido',                # particípio
            'ada', 'ados', 'adas',       # particípio plural/feminino
            'ída', 'idos', 'ídas',       # particípio plural/feminino
        ]
        
        for ending in conjugated_endings:
            if word.endswith(ending):
                return True
        
        # Check for present tense conjugations (more complex patterns)
        # 1st person: -o (amo, como, vivo)
        # 2nd person: -as, -es, -is (amas, comes, vives)
        # 3rd person: -a, -e, -i (ama, come, vive)
        if len(word) >= 4:
            last_two = word[-2:]
            
            # Present tense patterns (but avoid false positives)
            present_patterns = ['as', 'es', 'is', 'em', 'am']
            
            if last_two in present_patterns:
                return True
        
        return False
