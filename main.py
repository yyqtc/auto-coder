import os

def _init_project_structure():
    os.makedirs("experiment", exist_ok=True)
    os.makedirs("history", exist_ok=True)
    os.makedirs("opnion", exist_ok=True)
    os.makedirs("todo", exist_ok=True)
    os.makedirs("dist", exist_ok=True)


def main():
    _init_project_structure()


if __name__ == "__main__":
    main()
