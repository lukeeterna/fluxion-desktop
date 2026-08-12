from pathlib import Path
import re

p = Path('.github/workflows/voice-agent.yml')
lines = p.read_text(encoding='utf-8').splitlines(keepends=True)
out = []
mode = None
python_blocks = 0
heredocs = 0

for line in lines:
    if mode is None:
        out.append(line)
        stripped = line.lstrip(' ')
        indent = len(line) - len(stripped)
        marker = stripped.rstrip('\n')
        if indent >= 10 and marker == 'python -c "':
            mode = 'python'
            python_blocks += 1
        elif indent >= 10 and re.match(r"cat > .+ << 'EOF'$", marker):
            mode = 'heredoc'
            heredocs += 1
        continue

    marker = line.rstrip('\n')
    if marker == '':
        out.append('\n' if line.endswith('\n') else '')
    else:
        out.append('          ' + line)
    if (mode == 'python' and marker == '"') or (mode == 'heredoc' and marker == 'EOF'):
        mode = None

if mode is not None:
    raise SystemExit(f'unterminated block: {mode}')
if python_blocks != 6:
    raise SystemExit(f'expected 6 python blocks, got {python_blocks}')
if heredocs != 2:
    raise SystemExit(f'expected 2 heredocs, got {heredocs}')

new = ''.join(out)
if new == ''.join(lines):
    raise SystemExit('no changes applied')
p.write_text(new, encoding='utf-8')
print(f'PYTHON_BLOCKS_FIXED={python_blocks}')
print(f'HEREDOCS_FIXED={heredocs}')
