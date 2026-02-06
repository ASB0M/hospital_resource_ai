import json
import sys

def convert(nb_path):
    try:
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        out_path = nb_path.replace('.ipynb', '.py')
        with open(out_path, 'w', encoding='utf-8') as f:
            for cell in nb['cells']:
                if cell['cell_type'] == 'code':
                    source = ''.join(cell['source'])
                    f.write(source + '\n\n')
        print(f"Converted {nb_path} to {out_path}")
    except Exception as e:
        print(f"Error converting {nb_path}: {e}")

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        convert(arg)
