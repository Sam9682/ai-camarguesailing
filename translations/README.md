# Translations

This directory contains translation files for the Camargue Sailing website.

## Supported Languages

- English (en) - Default
- French (fr)

## Structure

```
translations/
├── fr/
│   └── LC_MESSAGES/
│       ├── messages.po  # French translations (source)
│       └── messages.mo  # Compiled translations (generated)
└── README.md
```

## Compiling Translations

Translations are automatically compiled when the application starts via `scripts/start.sh`.

To manually compile translations:

```bash
python scripts/compile_translations.py
```

## Adding New Translations

1. Edit `translations/fr/LC_MESSAGES/messages.po`
2. Add new msgid/msgstr pairs
3. Compile translations using the script above
4. Restart the application

## Using Translations in Templates

Use the `_()` function in Jinja2 templates:

```html
<h1>{{ _('Welcome to Camargue Sailing') }}</h1>
```

## Language Switching

Users can switch languages using the EN/FR links in the navigation bar. The selected language is stored in the session.
