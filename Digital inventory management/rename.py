with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('Nexus<span style="font-weight: 300;">ERP</span>', 'Inventory<span style="font-weight: 300;">System</span>')
content = content.replace('Enterprise Inventory Management', 'Inventory System')
content = content.replace('Enterprise Inventory Management</title>', 'Inventory System</title>')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
