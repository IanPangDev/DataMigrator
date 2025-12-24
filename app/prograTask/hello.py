import argparse

def main():
    parser = argparse.ArgumentParser(description="Script de ejemplo que recibe argumentos")
    parser.add_argument("--mode", type=int, help="Elimina o crea", required=True)
    
    args = parser.parse_args()
    
    print(f"HOLA MUNDO {args.mode}")
    
if __name__ == '__main__':
    main()