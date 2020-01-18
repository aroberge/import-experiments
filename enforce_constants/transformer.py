import re

assignment_pattern = re.compile(r"^\s*([\w][\w\d]*)\s*=\s*(.+)")
final_declaration_pattern = re.compile(r"^([\w][\w\d]*)\s*:\s*Final\s*=\s*(.+)")


def transform_assignment(source, mod_name, main=None):
    """Identifies simple assignments, including those with a Final type
       hint, and replace them by a special function call.
    """
    # First, ensure that if the module is meant to be run as main script,
    # anything like
    #     if __name__ == '__main__'
    # would still work
    if main is not None:
        if "'__main__'" in source:
            source = source.replace("'__main__'", f"'{main}'")
        elif '"__main__"' in source:
            source = source.replace('"__main__"', f'"{main}"')

    lines = source.split("\n")
    new_lines = ["import sys"]
    for line_number, line in enumerate(lines):
        match = re.search(assignment_pattern, line)
        match_final = re.search(final_declaration_pattern, line)
        if match:
            name = match.group(1)
            indent = len(line) - len(line.lstrip())
            value = match.group(2)
            new_lines.append(
                " " * indent
                + "sys.modules[__name__].__setattr__("
                + f"{repr(name)}, ({value}))"
            )
        elif match_final:
            name = match_final.group(1)
            value = match_final.group(2)
            new_lines.append(
                "sys.modules[__name__].__setattr__("
                + f"{repr(name)}, ({value}), final=True)"
            )
        else:
            new_lines.append(line)

    return "\n".join(new_lines)
