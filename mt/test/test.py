import click

@click.command()
@click.option('--name', help='name') 

def main(name):
    print("test: " + name)

if __name__ == "__main__":
    main()
