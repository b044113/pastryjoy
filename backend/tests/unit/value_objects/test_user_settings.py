"""Tests for UserSettings value object."""
import pytest

from src.domain.value_objects.user_settings import UserSettings


class TestUserSettings:
    """Test UserSettings value object."""

    def test_create_with_default_language(self) -> None:
        """Test creating settings with default language."""
        settings = UserSettings()
        assert settings.preferred_language == "en"

    def test_create_with_spanish(self) -> None:
        """Test creating settings with Spanish."""
        settings = UserSettings(preferred_language="es")
        assert settings.preferred_language == "es"

    def test_invalid_language_raises_error(self) -> None:
        """Test that invalid language raises ValueError."""
        with pytest.raises(ValueError, match="Invalid language"):
            UserSettings(preferred_language="fr")  # type: ignore

    def test_change_language(self) -> None:
        """Test changing language returns new instance."""
        settings = UserSettings(preferred_language="en")
        new_settings = settings.change_language("es")

        assert settings.preferred_language == "en"  # Original unchanged
        assert new_settings.preferred_language == "es"  # New instance

    def test_change_to_invalid_language(self) -> None:
        """Test changing to invalid language raises error."""
        settings = UserSettings()
        with pytest.raises(ValueError):
            settings.change_language("de")  # type: ignore

    def test_default_factory(self) -> None:
        """Test default factory method."""
        settings = UserSettings.default()
        assert settings.preferred_language == "en"

    def test_from_language_english(self) -> None:
        """Test creating from language string - English."""
        settings = UserSettings.from_language("en")
        assert settings.preferred_language == "en"

    def test_from_language_spanish(self) -> None:
        """Test creating from language string - Spanish."""
        settings = UserSettings.from_language("es")
        assert settings.preferred_language == "es"

    def test_from_language_with_region(self) -> None:
        """Test creating from language with region (en-US, es-ES)."""
        settings_en = UserSettings.from_language("en-US")
        assert settings_en.preferred_language == "en"

        settings_es = UserSettings.from_language("es-ES")
        assert settings_es.preferred_language == "es"

    def test_from_language_unsupported_falls_back_to_english(self) -> None:
        """Test that unsupported language falls back to English."""
        settings = UserSettings.from_language("fr")
        assert settings.preferred_language == "en"

    def test_immutability(self) -> None:
        """Test that settings is immutable (frozen dataclass)."""
        settings = UserSettings()
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            settings.preferred_language = "es"  # type: ignore
