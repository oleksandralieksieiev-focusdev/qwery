from tabulate import tabulate


def print_table(cols, rows):
    print(tabulate(rows, headers=cols, tablefmt="github", showindex=False))
