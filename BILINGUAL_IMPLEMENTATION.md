# Bilingual Implementation (EN/FR)

## Overview

The Camargue Sailing website now supports both English and French languages with a language switcher in the navigation bar.

## Implementation Details

### 1. Dependencies Added

- `Flask-Babel==4.0.0` - Flask extension for internationalization
- `Babel==2.14.0` - Python internationalization library

### 2. New Files Created

- `src/i18n.py` - Internationalization configuration module
- `translations/fr/LC_MESSAGES/messages.po` - French translations
- `scripts/compile_translations.py` - Script to compile .po to .mo files
- `translations/README.md` - Documentation for translations

### 3. Modified Files

- `src/app.py` - Added Babel initialization and language switching route
- `templates/base.html` - Added language switcher (EN/FR) and translation markers
- `templates/home.html` - Added translation markers for all text content
- `static/css/style.css` - Added styles for language switcher
- `scripts/start.sh` - Added translation compilation step
- `requirements.txt` - Added Flask-Babel and Babel dependencies

## Features

### Language Switcher

- Located in the top navigation bar
- Shows "EN | FR" with the active language highlighted
- Clicking switches the language and reloads the current page
- Language preference is stored in the session

### Translation System

- Uses Flask-Babel for internationalization
- Translations stored in `.po` files
- Automatically compiled to `.mo` files on application startup
- Falls back to English if translation not found

### Language Detection

Priority order:
1. User's explicit language choice (stored in session)
2. Browser's Accept-Language header
3. Default to English

## Usage

### For Users

1. Visit the website
2. Click "EN" or "FR" in the top navigation bar
3. The page will reload in the selected language
4. Language preference persists during the session

### For Developers

#### Adding New Translations

1. Edit `translations/fr/LC_MESSAGES/messages.po`
2. Add new translation pairs:
   ```
   msgid "English text"
   msgstr "Texte français"
   ```
3. Restart the application (translations are auto-compiled)

#### Using Translations in Templates

```html
<!-- Simple text -->
<h1>{{ _('Welcome') }}</h1>

<!-- Text with HTML -->
<p>{{ _('This is a paragraph') }}</p>

<!-- In attributes -->
<a href="/about" title="{{ _('About Us') }}">{{ _('About') }}</a>
```

## Current Translation Coverage

The following pages/sections are fully translated:

- Navigation menu
- Authentication (Sign In, Sign Up, Sign Out)
- Home page (all sections)
- Footer

## Next Steps

To add translations to other pages:

1. Add translation markers `{{ _('text') }}` to templates
2. Add corresponding translations to `messages.po`
3. Restart the application

## Testing

1. Start the application
2. Visit the home page
3. Click "FR" - page should display in French
4. Click "EN" - page should display in English
5. Verify language preference persists across page navigation

## Technical Notes

- Language code is stored in `session['language']`
- Translations are compiled at startup via `scripts/start.sh`
- The `get_locale()` function in `src/i18n.py` determines the active language
- Translation files follow GNU gettext format (.po/.mo)
