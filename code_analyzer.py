import ast
import os
import sys
import re


def check_length(path_to_file, line_number, line):
    if len(line) > 79:
        print(f'{path_to_file}: Line {line_number + 1}: S001 Too long')


def check_indentation(path_to_file, line_number, line):
    indentation_len = len(line) - len(str.lstrip(line))
    if indentation_len % 4 != 0:
        print(f'{path_to_file}: Line {line_number + 1}: S002 Indentation is not a multiple of four')


def check_semicolon_after_statement(path_to_file, line_number, line):
    if str.split(line, '#')[0].rstrip().endswith(';'):
        print(f'{path_to_file}: Line {line_number + 1}: S003 Unnecessary semicolon')


def check_inline_comment(path_to_file, line_number, line):
    statement_line_till_comment = str.split(line, '#')[0]
    whitespaces_count = len(statement_line_till_comment) - len(str.rstrip(statement_line_till_comment))
    if line.__contains__('#') and not line.lstrip().startswith('#') and whitespaces_count < 2:
        print(
            f'{path_to_file}: Line {line_number + 1}: S004 At least two spaces required before in{path_to_analyze}: Line comments')


def check_todo(path_to_file, line_number, line):
    if str.__contains__(line, '#') and str.split(line, '#', maxsplit=1)[1].lower().__contains__("todo"):
        print(f'{path_to_file}: Line {line_number + 1}: S005 TODO found')


def check_lines_preceding(path_to_file, line_number, line, lines):
    if len(line) != 0 and line_number > 2 \
            and len(str.strip(lines[line_number - 1])) == 0 \
            and len(str.strip(lines[line_number - 2])) == 0 \
            and len(str.strip(lines[line_number - 3])) == 0:
        print(f'{path_to_file}: Line {line_number + 1}: S006 More than two blank lines used before this line')


def too_many_spaces_after_construction_name(path_to_file, line_number, line):
    if (str.startswith(str.strip(line), "class") and re.match("class {2}", line) is not None) or \
            (str.startswith(str.strip(line), "def") and re.match("def {2}", str.strip(line)) is not None):
        print(f'{path_to_file}: Line {line_number + 1}: S007 Too many spaces after class or def')


def class_name_camel_case(path_to_file, line_number, line):
    if str.startswith(str.strip(line), "class") and \
            re.match("class *([A-Z][a-z0-9]+)+\\(*([A-Z][a-z0-9]+)*\\)*", str.strip(line)) is None:
        print(f'{path_to_file}: Line {line_number + 1}: S008 Class name should use CamelCase')


def def_snake_case(path_to_file, line_number, line):
    if str.startswith(str.strip(line), "def") and re.match("def *[a-z_]+(?:_[a-zA-Z]+)*", str.strip(line)) is None:
        print(f'{path_to_file}: Line {line_number + 1}: S009 Function name should use snake_case')


def snake_case(path_to_file, line_number, line):
    if re.match("[a-z_]+(?:_[a-zA-Z]+)*", str.strip(line)) is None:
        print(f'{path_to_file}: Line {line_number}: S010 Should be snake_case')


def snake_case_var(path_to_file, line_number, line):
    if re.match("[a-z_]+(?:_[a-zA-Z]+)*", str.strip(line)) is None:
        print(f'{path_to_file}: Line {line_number}: S011 var snake_case')


def snake_case_def(path_to_file, root_node):
    if isinstance(root_node, ast.FunctionDef):
        for class_node in [a.arg for a in root_node.args.args]:
            snake_case(path_to_file, root_node.lineno, class_node)
        for class_node in [a for a in root_node.args.defaults]:
            if type(class_node) in (ast.List, ast.Set, ast.Dict):
                print(f'{path_to_file}: Line {root_node.lineno}: S012 mutable')
    if isinstance(root_node, ast.Assign) and type(root_node.targets[0]) is ast.Name:
        snake_case_var(path_to_file, root_node.lineno, root_node.targets[0].id)
    if hasattr(root_node, "body"):
        for node in root_node.body:
            snake_case_def(path_to_file, node)


def analyze_file(path_to_file):
    source_code_file = open(path_to_file, 'r')

    lines = source_code_file.readlines()

    for i in range(0, len(lines)):
        check_length(path_to_file, i, lines[i].rstrip())
        check_indentation(path_to_file, i, lines[i].rstrip())
        check_semicolon_after_statement(path_to_file, i, lines[i].rstrip())
        check_inline_comment(path_to_file, i, lines[i].rstrip())
        check_todo(path_to_file, i, lines[i].rstrip())
        check_lines_preceding(path_to_file, i, lines[i].rstrip(), lines)
        too_many_spaces_after_construction_name(path_to_file, i, lines[i].rstrip())
        class_name_camel_case(path_to_file, i, lines[i].rstrip())
        def_snake_case(path_to_file, i, lines[i].rstrip())

    root_node = ast.parse(str.join("", lines))
    snake_case_def(path_to_file, root_node)

    source_code_file.close()


if __name__ == '__main__':
    args = sys.argv

    path_to_analyze = args[1]

    if os.path.isdir(path_to_analyze):
        files = os.listdir(path_to_analyze)
        files.sort()
        for file_name in files:
            if str.strip(file_name).endswith(".py"):
                analyze_file(path_to_analyze + os.sep + file_name)
    else:
        analyze_file(path_to_analyze)
