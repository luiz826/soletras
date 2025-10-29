#!/usr/bin/env python3
"""
Pre-process words with SpaCy and save to disk.
Run this script locally BEFORE deploying to generate the filtered word lists.

Usage:
    uv run python preprocess_words.py
    
This will:
1. Download all word sources
2. Apply SpaCy filters (plurals, conjugated verbs)
3. Save filtered results to data/preprocessed/
4. These files can be committed and deployed (no SpaCy needed in production)
"""

import pickle
import logging
from pathlib import Path
from src.config import get_config
from src.word_loader import WordLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def preprocess_words():
    """Pre-process all word combinations and save to disk."""
    
    # Get configuration
    config = get_config()
    
    # Create output directory
    output_dir = Path('data/preprocessed')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("="*60)
    logger.info("Starting word pre-processing")
    logger.info("="*60)
    
    # Initialize word loader
    logger.info("Loading words from sources...")
    word_loader = WordLoader(config.WORD_SOURCES)
    word_loader.load()
    
    logger.info(f"Loaded {word_loader.word_count:,} unique words")
    
    # Define filter combinations to pre-process
    filter_combinations = [
        {'filter_plurals': False, 'filter_conjugated_verbs': False},
        {'filter_plurals': True, 'filter_conjugated_verbs': False},
        {'filter_plurals': False, 'filter_conjugated_verbs': True},
        {'filter_plurals': True, 'filter_conjugated_verbs': True},
    ]
    
    logger.info(f"\nPre-processing {len(filter_combinations)} filter combinations...")
    
    original_word_count = word_loader.word_count
    
    for i, filters in enumerate(filter_combinations, 1):
        remove_plurals = filters['filter_plurals']
        remove_conjugated_verbs = filters['filter_conjugated_verbs']
        
        # Generate filename
        filename = f"words_p{int(remove_plurals)}_v{int(remove_conjugated_verbs)}.pkl"
        output_path = output_dir / filename
        
        logger.info(f"\n[{i}/{len(filter_combinations)}] Processing:")
        logger.info(f"  - Remove plurals: {remove_plurals}")
        logger.info(f"  - Remove conjugated verbs: {remove_conjugated_verbs}")
        
        # Filter words (modifies word_loader.words in place)
        removed = word_loader.filter_words(
            remove_plurals=remove_plurals,
            remove_conjugated_verbs=remove_conjugated_verbs
        )
        
        # Get filtered words
        filtered_words = word_loader.words
        
        # Save to disk
        with open(output_path, 'wb') as f:
            pickle.dump(filtered_words, f)
        
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        logger.info(f"  ✅ Saved {len(filtered_words):,} words to {filename} ({file_size_mb:.2f} MB)")
        logger.info(f"      Removed {removed:,} words from original {original_word_count:,}")
        
        # Reload original words for next iteration
        word_loader.load()
    
    # Save source words (unfiltered) as well
    source_path = output_dir / 'source_words.pkl'
    with open(source_path, 'wb') as f:
        pickle.dump(word_loader.words, f)
    
    file_size_mb = source_path.stat().st_size / (1024 * 1024)
    logger.info(f"\n✅ Saved source words to source_words.pkl ({file_size_mb:.2f} MB)")
    
    logger.info("\n" + "="*60)
    logger.info("Pre-processing complete!")
    logger.info("="*60)
    logger.info(f"\nGenerated files in {output_dir}:")
    for file_path in sorted(output_dir.glob('*.pkl')):
        size_mb = file_path.stat().st_size / (1024 * 1024)
        logger.info(f"  - {file_path.name} ({size_mb:.2f} MB)")
    
    logger.info("\n📝 Next steps:")
    logger.info("  1. git add data/preprocessed/")
    logger.info("  2. git commit -m 'Add pre-processed word lists'")
    logger.info("  3. git push origin master")
    logger.info("  4. Deploy to Render (no SpaCy processing needed!)")


if __name__ == '__main__':
    preprocess_words()
