import json
import os
import shutil

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_path = os.path.join(root_dir, 'index.html')
    public_index_path = os.path.join(root_dir, 'public', 'index.html')
    readme_path = os.path.join(root_dir, 'README.md')

    # 1. Update index.html
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        ('39-Page Architecture Treatise', '24-Page Architecture Treatise'),
        ('39-Page Architectural Treatise', '24-Page Architectural Treatise'),
        ('39-Page IEEE Architecture Treatise', '24-Page IEEE Architecture Treatise'),
        ('in the 39-page foundational', 'in the 24-page foundational'),
        ('202611052791. 39-page architectural specification}', '202611052791. 24-page architectural specification}'),
        ('Architectural Treatise (39-Page)', 'Architectural Treatise (24-Page)'),
    ]

    for old, new in replacements:
        count = content.count(old)
        content = content.replace(old, new)
        print(f'Replaced {count} instances of "{old}" with "{new}"')

    # Update window.EMBEDDED_CODE_SNIPPETS
    for line in content.splitlines():
        if 'window.EMBEDDED_CODE_SNIPPETS =' in line:
            old_line = line
            json_str = line.split('window.EMBEDDED_CODE_SNIPPETS =', 1)[1].strip()
            if json_str.endswith(';'):
                json_str = json_str[:-1]
            data = json.loads(json_str)

            for rel_path in data.keys():
                full_path = os.path.join(root_dir, rel_path)
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as sf:
                        code_text = sf.read()
                    data[rel_path]['content'] = code_text
                    data[rel_path]['lines'] = len(code_text.splitlines())
                    data[rel_path]['size_bytes'] = len(code_text.encode('utf-8'))
                    print(f'Updated snippet for {rel_path} ({data[rel_path]["lines"]} lines)')

            new_json_str = json.dumps(data)
            new_line = f'    window.EMBEDDED_CODE_SNIPPETS = {new_json_str};'
            content = content.replace(old_line, new_line)
            print('Updated window.EMBEDDED_CODE_SNIPPETS in index.html')
            break

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # 2. Copy index.html to public/index.html
    shutil.copyfile(index_path, public_index_path)
    print('Copied index.html to public/index.html')

    # 3. Update README.md
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    readme_replacements = [
        ('Complete 39-page formally verified IEEE manuscript', 'Complete 24-page formally verified IEEE manuscript'),
        ('39-Page Primary IEEE Architecture Manuscript', '24-Page Primary IEEE Architecture Manuscript'),
    ]

    for old, new in readme_replacements:
        count = readme_content.count(old)
        readme_content = readme_content.replace(old, new)
        print(f'README: Replaced {count} instances of "{old}" with "{new}"')

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print('Web synchronization script completed successfully.')

if __name__ == '__main__':
    main()
