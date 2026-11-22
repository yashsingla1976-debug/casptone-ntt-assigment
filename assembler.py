"""Hack assembler (Nand to Tetris) with K-feature 1:
clear error messages with line numbers instead of crashing.
Usage: python assembler.py Prog.asm   ->  writes Prog.hack
"""
import sys

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "DM": "011", "A": "100", "AM": "101",
        "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

SYMBOLS_INIT = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
                "SCREEN": 16384, "KBD": 24576}
SYMBOLS_INIT.update({f"R{i}": i for i in range(16)})


def valid_symbol(s):
    if not s or s[0].isdigit():
        return False
    return all(c.isalnum() or c in "_.$:" for c in s)


def clean(line):
    """Remove comments and all whitespace."""
    return "".join(line.split("//")[0].split())


def assemble(lines):
    errors = []
    symbols = dict(SYMBOLS_INIT)

    # ---------- First pass: labels ----------
    program = []          # (line_number, cleaned_text)
    for n, raw in enumerate(lines, 1):
        text = clean(raw)
        if not text:
            continue
        if text.startswith("("):
            if not text.endswith(")") or not valid_symbol(text[1:-1]):
                errors.append(f"Line {n}: invalid instruction")
                continue
            label = text[1:-1]
            if label in symbols:
                errors.append(f"Line {n}: invalid instruction (label '{label}' already defined)")
            else:
                symbols[label] = len(program)
            continue
        program.append((n, text))

    # ---------- Second pass: translate ----------
    out = []
    next_var = 16
    for n, text in program:
        if text.startswith("@"):
            val = text[1:]
            if val.isdigit():
                num = int(val)
                if num > 32767:
                    errors.append(f"Line {n}: invalid instruction (number too large)")
                    continue
            elif valid_symbol(val):
                if val not in symbols:
                    symbols[val] = next_var
                    next_var += 1
                num = symbols[val]
            else:
                errors.append(f"Line {n}: invalid instruction")
                continue
            out.append(format(num, "016b"))
        else:
            dest, comp, jump = "", text, ""
            if "=" in comp:
                dest, comp = comp.split("=", 1)
            if ";" in comp:
                comp, jump = comp.split(";", 1)
            if dest not in DEST or comp not in COMP or jump not in JUMP:
                errors.append(f"Line {n}: invalid instruction")
                continue
            out.append("111" + COMP[comp] + DEST[dest] + JUMP[jump])
    return out, errors


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path) as f:
            lines = f.readlines()
    except OSError as e:
        print(f"Cannot open file: {e}")
        sys.exit(1)

    out, errors = assemble(lines)
    if errors:
        for e in errors:
            print(e)
        print(f"{len(errors)} error(s) found. No .hack file written.")
        sys.exit(1)

    hack = path[:-4] + ".hack"
    with open(hack, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"Wrote {len(out)} instructions to {hack}")


if __name__ == "__main__":
    main()
