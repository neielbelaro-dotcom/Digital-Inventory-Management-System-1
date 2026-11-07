with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace text-muted in labels with text-light opacity-75
content = content.replace('label class="form-label text-muted', 'label class="form-label text-light opacity-75')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
