import filecmp
import os
from filecmp import dircmp
from jinja2 import Environment, FileSystemLoader
# https://docs.python.org/3/library/filecmp.html


def build_matrix(directory_path):
    authors = [author for author in os.listdir(
        directory_path) if os.path.isdir(os.path.join(directory_path, author))]

    matrix_opmerkingen = {author: {other_author: []
                                   for other_author in authors} for author in authors}

    for author in authors:
        author_path = os.path.join(directory_path, author)
        other_authors = [
            other_author for other_author in authors if other_author != author]

        for other_author in other_authors:
            other_author_path = os.path.join(directory_path, other_author)

            comparison = dircmp(author_path, other_author_path)

            common_files = comparison.common_files
            for common_file in common_files:
                file_path = os.path.join(author_path, common_file)
                if filecmp.cmp(file_path, os.path.join(other_author_path, common_file)):
                    matrix_opmerkingen[author][other_author].append(
                        f"Identieke file {common_file}")

    return authors, matrix_opmerkingen


def generate_report(auteurs, matrix_opmerkingen):
    alias_mapping = {auteur: f"student_{index + 1}" for index,
                     auteur in enumerate(auteurs)}

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=True
    )

    template = env.get_template("outputtemplate.html")
    html_output = template.render(
        matrix_opmerkingen=matrix_opmerkingen, alias_mapping=alias_mapping, auteurs=auteurs)

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