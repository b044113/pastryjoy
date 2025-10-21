"""User settings value object."""
from dataclasses import dataclass
from typing import Literal


# Supported languages
SupportedLanguage = Literal["en", "es"]


@dataclass(frozen=True)
class UserSettings:
    """User settings value object.

    This is an immutable value object that represents user preferences.
    Currently supports language preference, but designed to be extensible.
    """

    preferred_language: SupportedLanguage = "en"

    def __post_init__(self) -> None:
        """Validate user settings."""
        if self.preferred_language not in ("en", "es"):
            raise ValueError(
                f"Invalid language: {self.preferred_language}. "
                f"Supported languages: en, es"
            )

    def change_language(self, new_language: SupportedLanguage) -> "UserSettings":
        """Create a new UserSettings with updated language.

        Args:
            new_language: The new preferred language

        Returns:
            A new UserSettings instance with updated language

        Raises:
            ValueError: If language is not supported
        """
        return UserSettings(preferred_language=new_language)

    @classmethod
    def default(cls) -> "UserSettings":
        """Create default user settings.

        Returns:
            UserSettings with English as default language
        """
        return cls(preferred_language="en")

    @classmethod
    def from_language(cls, language: str) -> "UserSettings":
        """Create UserSettings from language string.

        Args:
            language: Language code (en, es)

        Returns:
            UserSettings with specified language

        Raises:
            ValueError: If language is not supported
        """
        # Normalize language (handle en-US, es-ES, etc.)
        normalized = language.lower().split("-")[0]

        if normalized not in ("en", "es"):
            # Fall back to English if unsupported
            normalized = "en"

        return cls(preferred_language=normalized)  # type: ignore
