with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix table cells
content = content.replace('<td class="ps-4 text-muted">', '<td class="ps-4 text-light opacity-75">')
content = content.replace('<td class="text-muted">', '<td class="text-light opacity-75">')
content = content.replace('<td class="text-muted small text-end pe-4">', '<td class="text-light opacity-75 small text-end pe-4">')
content = content.replace('text-muted small', 'text-light opacity-75 small')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
