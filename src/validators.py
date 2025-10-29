"""
Request validation module.
Validates and sanitizes API request parameters.
"""

from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class SearchParams:
    """Validated search parameters."""
    allowed_letters: str
    required_letter: str
    min_length: int
    max_length: Optional[int] = None  # Optional maximum word length


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class RequestValidator:
    """Validates search request parameters."""
    
    def __init__(self, min_word_length: int = 1, max_word_length: int = 100):
        """
        Initialize the validator.
        
        Args:
            min_word_length: Minimum allowed word length
            max_word_length: Maximum allowed word length
        """
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
    
    def validate_search_params(
        self,
        allowed_letters: Optional[str],
        required_letter: Optional[str],
        min_length: Optional[str],
        max_length: Optional[str] = None
    ) -> SearchParams:
        """
        Validate and normalize search parameters.
        
        Args:
            allowed_letters: String of allowed letters (can be None)
            required_letter: Required letter (can be None)
            min_length: Minimum length as string (can be None)
            max_length: Maximum length as string (optional)
        
        Returns:
            SearchParams object with validated parameters
        
        Raises:
            ValidationError: If any parameter is invalid
        """
        # Check required parameters
        if not allowed_letters:
            raise ValidationError('Missing required parameter: allowed_letters')
        
        if not required_letter:
            raise ValidationError('Missing required parameter: required_letter')
        
        if not min_length:
            raise ValidationError('Missing required parameter: min_length')
        
        # Normalize string parameters
        allowed_letters = allowed_letters.lower().strip()
        required_letter = required_letter.lower().strip()
        
        # Validate allowed_letters
        if not allowed_letters:
            raise ValidationError('allowed_letters cannot be empty')
        
        if not allowed_letters.isalpha():
            raise ValidationError('allowed_letters must contain only letters')
        
        # Validate required_letter
        if len(required_letter) != 1:
            raise ValidationError('required_letter must be a single character')
        
        if not required_letter.isalpha():
            raise ValidationError('required_letter must be a letter')
        
        # Validate required_letter is in allowed_letters
        if required_letter not in allowed_letters:
            raise ValidationError('required_letter must be in allowed_letters')
        
        # Validate min_length
        try:
            min_length_int = int(min_length)
        except ValueError:
            raise ValidationError('min_length must be a valid integer')
        
        if min_length_int < self.min_word_length:
            raise ValidationError(
                f'min_length must be at least {self.min_word_length}'
            )
        
        if min_length_int > self.max_word_length:
            raise ValidationError(
                f'min_length must be at most {self.max_word_length}'
            )
        
        # Validate max_length (optional)
        max_length_int = None
        if max_length:
            try:
                max_length_int = int(max_length)
            except ValueError:
                raise ValidationError('max_length must be a valid integer')
            
            if max_length_int < self.min_word_length:
                raise ValidationError(
                    f'max_length must be at least {self.min_word_length}'
                )
            
            if max_length_int > self.max_word_length:
                raise ValidationError(
                    f'max_length must be at most {self.max_word_length}'
                )
            
            if max_length_int < min_length_int:
                raise ValidationError(
                    'max_length must be greater than or equal to min_length'
                )
        
        return SearchParams(
            allowed_letters=allowed_letters,
            required_letter=required_letter,
            min_length=min_length_int,
            max_length=max_length_int
        )
