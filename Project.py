from jinja2 import Environment, FileSystemLoader


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
    auteurs = ["Vincent", "Alice", "Bob"]

    matrix_opmerkingen = {auteur: {andere_auteur: []
                                   for andere_auteur in auteurs} for auteur in auteurs}
    matrix_opmerkingen["Vincent"]["Alice"] = ["dezelfde verdachte fout"]
    matrix_opmerkingen["Alice"]["Bob"] = ["/"]

    print(matrix_opmerkingen)

    generate_report(auteurs, matrix_opmerkingen)
