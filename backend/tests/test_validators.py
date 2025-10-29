"""
Unit tests for the RequestValidator class.
"""

import pytest
from src.validators import RequestValidator, ValidationError, SearchParams


class TestRequestValidator:
    """Test suite for RequestValidator."""
    
    @pytest.fixture
    def validator(self):
        """Fixture providing a RequestValidator instance."""
        return RequestValidator(min_word_length=1, max_word_length=100)
    
    def test_init(self):
        """Test RequestValidator initialization."""
        validator = RequestValidator(min_word_length=3, max_word_length=50)
        assert validator.min_word_length == 3
        assert validator.max_word_length == 50
    
    def test_validate_search_params_valid(self, validator):
        """Test validation with valid parameters."""
        params = validator.validate_search_params(
            allowed_letters="abcdefg",
            required_letter="a",
            min_length="5"
        )
        
        assert isinstance(params, SearchParams)
        assert params.allowed_letters == "abcdefg"
        assert params.required_letter == "a"
        assert params.min_length == 5
    
    def test_validate_search_params_normalization(self, validator):
        """Test parameter normalization (lowercase, strip)."""
        params = validator.validate_search_params(
            allowed_letters="  ABCDEFG  ",
            required_letter="  A  ",
            min_length="5"
        )
        
        assert params.allowed_letters == "abcdefg"
        assert params.required_letter == "a"
    
    def test_validate_missing_allowed_letters(self, validator):
        """Test validation with missing allowed_letters."""
        with pytest.raises(ValidationError, match="Missing required parameter: allowed_letters"):
            validator.validate_search_params(
                allowed_letters=None,
                required_letter="a",
                min_length="5"
            )
    
    def test_validate_missing_required_letter(self, validator):
        """Test validation with missing required_letter."""
        with pytest.raises(ValidationError, match="Missing required parameter: required_letter"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter=None,
                min_length="5"
            )
    
    def test_validate_missing_min_length(self, validator):
        """Test validation with missing min_length."""
        with pytest.raises(ValidationError, match="Missing required parameter: min_length"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter="a",
                min_length=None
            )
    
    def test_validate_empty_allowed_letters(self, validator):
        """Test validation with empty allowed_letters."""
        with pytest.raises(ValidationError, match="allowed_letters cannot be empty"):
            validator.validate_search_params(
                allowed_letters="   ",
                required_letter="a",
                min_length="5"
            )
    
    def test_validate_allowed_letters_non_alpha(self, validator):
        """Test validation with non-alphabetic allowed_letters."""
        with pytest.raises(ValidationError, match="allowed_letters must contain only letters"):
            validator.validate_search_params(
                allowed_letters="abc123",
                required_letter="a",
                min_length="5"
            )
    
    def test_validate_required_letter_not_single(self, validator):
        """Test validation with multi-character required_letter."""
        with pytest.raises(ValidationError, match="required_letter must be a single character"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter="ab",
                min_length="5"
            )
    
    def test_validate_required_letter_non_alpha(self, validator):
        """Test validation with non-alphabetic required_letter."""
        with pytest.raises(ValidationError, match="required_letter must be a letter"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter="1",
                min_length="5"
            )
    
    def test_validate_required_letter_not_in_allowed(self, validator):
        """Test validation when required_letter not in allowed_letters."""
        with pytest.raises(ValidationError, match="required_letter must be in allowed_letters"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter="z",
                min_length="5"
            )
    
    def test_validate_min_length_invalid_integer(self, validator):
        """Test validation with non-integer min_length."""
        with pytest.raises(ValidationError, match="min_length must be a valid integer"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter="a",
                min_length="not_a_number"
            )
    
    def test_validate_min_length_too_small(self, validator):
        """Test validation with min_length below minimum."""
        with pytest.raises(ValidationError, match="min_length must be at least 1"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter="a",
                min_length="0"
            )
    
    def test_validate_min_length_too_large(self, validator):
        """Test validation with min_length above maximum."""
        with pytest.raises(ValidationError, match="min_length must be at most 100"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter="a",
                min_length="101"
            )
    
    def test_validate_custom_limits(self):
        """Test validator with custom min/max word length."""
        validator = RequestValidator(min_word_length=5, max_word_length=20)
        
        with pytest.raises(ValidationError, match="min_length must be at least 5"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter="a",
                min_length="3"
            )
        
        with pytest.raises(ValidationError, match="min_length must be at most 20"):
            validator.validate_search_params(
                allowed_letters="abc",
                required_letter="a",
                min_length="25"
            )


class TestSearchParams:
    """Test suite for SearchParams dataclass."""
    
    def test_search_params_creation(self):
        """Test SearchParams creation."""
        params = SearchParams(
            allowed_letters="abc",
            required_letter="a",
            min_length=5
        )
        
        assert params.allowed_letters == "abc"
        assert params.required_letter == "a"
        assert params.min_length == 5
