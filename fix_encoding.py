import re

# Read the file
try:
    with open('app.py', 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Define replacements for corrupted emojis and symbols
    replacements = [
        ('ðŸŽ™ï¸', '🎙️'),
        ('ðŸ¦™', '🦙'),
        ('ðŸ"'', '🔒'),
        ('ðŸŒŸ', '⭐'),
        ('ðŸ"', '🔑'),
        ('ðŸ"', '📝'),
        ('ðŸ"Š', '📊'),
        ('ðŸ"ˆ', '📈'),
        ('ðŸ"', '📁'),
        ('â€¢', '•')
    ]

    # Apply all replacements
    for old, new in replacements:
        content = content.replace(old, new)

    # Write back the corrected content
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print('Emoji encoding issues fixed successfully!')

except Exception as e:
    print(f'Error: {e}')
