import ast
import filecmp
# https://docs.python.org/3/library/filecmp.html
import os
import re
from jinja2 import Environment, FileSystemLoader
from spellchecker import SpellChecker
from libcst import Comment, TrailingWhitespace, parse_module
from libcst import CSTTransformer, RemoveFromParent


class CommentRemovalTransformer(CSTTransformer):
    def leave_Comment(self, original_node: Comment, updated_node: Comment) -> Comment:
        return RemoveFromParent()

    def leave_TrailingWhitespace(self, original_node: TrailingWhitespace, updated_node: TrailingWhitespace):
        return RemoveFromParent()


def extract_single_line_comments(file_path):
    comments = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            match = re.match(r'^\s*#\s*(.*)$', line)
            if match:
                comment_text = match.group(1)
                comments.append(comment_text)
    return comments


def remove_comments(source_code):
    module = parse_module(source_code)
    transformer = CommentRemovalTransformer()
    transformed_module = module.visit(transformer)
    return transformed_module.code, module


def compare_ast(source_code1, source_code2):
    _, cst1 = remove_comments(source_code1)
    _, cst2 = remove_comments(source_code2)

    ast1 = ast.parse(cst1.code)
    ast2 = ast.parse(cst2.code)

    return ast.dump(ast1) == ast.dump(ast2)


def build_matrix(directory_path):
    authors = [author for author in os.listdir(
        directory_path) if os.path.isdir(os.path.join(directory_path, author))]

    matrix_opmerkingen = {author: {other_author: []
                                   for other_author in authors} for author in authors}

    spell = SpellChecker()

    for author in authors:
        author_path = os.path.join(directory_path, author)
        other_authors = [
            other_author for other_author in authors if other_author != author]

        for other_author in other_authors:
            other_author_path = os.path.join(directory_path, other_author)
            comparison = filecmp.dircmp(author_path, other_author_path)

            common_files = comparison.common_files
            common_files.sort()

            for common_file in common_files:
                file_path = os.path.join(author_path, common_file)
                other_file_path = os.path.join(other_author_path, common_file)

                if filecmp.cmp(file_path, other_file_path):
                    with open(file_path, 'r', encoding='utf-8') as file1, open(other_file_path, 'r', encoding='utf-8') as file2:
                        source_code1 = file1.read()
                        source_code2 = file2.read()

                        identical_ast = compare_ast(source_code1, source_code2)

                        if identical_ast:
                            matrix_opmerkingen[author][other_author].append(
                                f"Identieke abstracte syntaxboom in file {common_file}")

                            if common_file != file_path:
                                matrix_opmerkingen[author][other_author].append(
                                    f"Identieke bestandsnamen: {common_file}")

                            if source_code1 != source_code2:
                                matrix_opmerkingen[author][other_author].append(
                                    f"Identieke bestandsinhoud in file {common_file}")

                            comments_author = set(
                                extract_single_line_comments(file_path))
                            comments_other_author = set(
                                extract_single_line_comments(other_file_path))

                            if comments_author == comments_other_author and comments_author:
                                matrix_opmerkingen[author][other_author].append(
                                    f"Identieke single-line comments in file {common_file}: {', '.join(comments_author)}")

                            comments_author_words = set(
                                [word.lower() for comment in comments_author for word in comment.split()])
                            comments_other_author_words = set(
                                [word.lower() for comment in comments_other_author for word in comment.split()])
                            common_comment_words = comments_author_words.intersection(
                                comments_other_author_words)

                            misspelled_words = set(
                                spell.unknown(common_comment_words))
                            if misspelled_words:
                                matrix_opmerkingen[author][other_author].append(
                                    f"Identieke spelfouten in comments in file {common_file}: {', '.join(misspelled_words)}")

    return authors, matrix_opmerkingen


def generate_report(authors, matrix_opmerkingen):
    alias_mapping = {auteur: f"student_{index + 1}" for index,
                     auteur in enumerate(authors)}

    env = Environment(loader=FileSystemLoader("."), autoescape=True)

    template = env.get_template("outputtemplate.html")
    html_output = template.render(
        matrix_opmerkingen=matrix_opmerkingen, alias_mapping=alias_mapping, auteurs=authors)

    output_file_name = input(
        "Geef de naam van het outputbestand (bijv. output.html): ")

    with open(output_file_name, "w") as output_file:
        output_file.write(html_output)

    print(f"Rapport gegenereerd en opgeslagen als {output_file_name}")


if __name__ == "__main__":
    directory_path = input(
        "Geef het pad naar de directory met auteur mappen: ")
    auteurs, matrix_opmerkingen = build_matrix(directory_path)
    print(matrix_opmerkingen)
    generate_report(auteurs, matrix_opmerkingen)
