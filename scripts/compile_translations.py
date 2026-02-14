#!/usr/bin/env python3
"""
Compile translation files for the application.

This script compiles .po files to .mo files for Flask-Babel.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from babel.messages.pofile import read_po
    from babel.messages.mofile import write_mo
except ImportError:
    print("Error: babel is not installed. Install it with: pip install Babel")
    sys.exit(1)


def compile_translations():
    """Compile all .po files to .mo files."""
    translations_dir = project_root / 'translations'
    
    if not translations_dir.exists():
        print(f"Error: Translations directory not found: {translations_dir}")
        return False
    
    success = True
    for po_file in translations_dir.rglob('*.po'):
        mo_file = po_file.with_suffix('.mo')
        
        try:
            print(f"Compiling {po_file} -> {mo_file}")
            
            with open(po_file, 'rb') as f:
                catalog = read_po(f)
            
            with open(mo_file, 'wb') as f:
                write_mo(f, catalog)
            
            print(f"  ✓ Successfully compiled {mo_file.name}")
        except Exception as e:
            print(f"  ✗ Error compiling {po_file}: {e}")
            success = False
    
    return success


if __name__ == '__main__':
    print("=" * 60)
    print("Compiling Translation Files")
    print("=" * 60)
    
    if compile_translations():
        print("\n✓ All translations compiled successfully")
        sys.exit(0)
    else:
        print("\n✗ Some translations failed to compile")
        sys.exit(1)
