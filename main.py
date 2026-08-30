from banco import criar_tabela, adicionar_gasto, listar_gastos, total_gasto
from ia import gerar_analise

def exibir_gastos():
    gastos = listar_gastos()
    if not gastos:
        print("Nenhum gasto registrado ainda.\n")
        return
    print("\n--- Seus gastos ---")
    for g in gastos:
        print(f"[{g[0]}] {g[4]} - {g[1]}: R$ {g[2]:.2f} ({g[3] or 'sem categoria'})")
    print(f"\nTotal gasto: R$ {total_gasto():.2f}\n")

def menu():
    criar_tabela()
    while True:
        print("=== Controle de Gastos ===")
        print("1 - Adicionar gasto")
        print("2 - Listar gastos")
        print("3 - Gerar análise com IA")
        print("4 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            descricao = input("Descrição do gasto: ").strip()
            if not descricao:
                print("Descrição não pode ser vazia.\n")
                continue
            try:
                valor = float(input("Valor (ex: 25.50): ").replace(",", "."))
            except ValueError:
                print("Valor inválido, tente novamente.\n")
                continue
            categoria = input("Categoria (opcional, Enter pra pular): ").strip() or None
            adicionar_gasto(descricao, valor, categoria)
            print("Gasto registrado!\n")

        elif opcao == "2":
            exibir_gastos()

        elif opcao == "3":
            gastos = listar_gastos()
            print("\n--- Análise da IA ---")
            print(gerar_analise(gastos))
            print()

        elif opcao == "4":
            print("Até mais!")
            break

        else:
            print("Opção inválida, tente novamente.\n")

if __name__ == "__main__":
    menu()
