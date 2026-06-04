from database import (
    initialize_database,
    add_card,
    remove_card,
    get_card,
    get_duplicates,
    get_stats,
    get_missing
)


def print_help():
    print("""
Komendy:

add <nr>
remove <nr>

show <nr>
show (NAT) - nationality 3 letters

duplicates
missing
stats

exit
""")


def main():
    initialize_database()

    print("Card Tracker")
    print_help()

    while True:
        command = input("> ").strip()

        if not command:
            continue

        parts = command.split()

        match parts[0]:

            case "add":
                for num in parts[1:]:
                    add_card(int(num))

                print("Dodano.")

            case "remove":
                for num in parts[1:]:
                    remove_card(int(num))

                print("Usunięto.")

            case "show":
                if parts[1][0] == '(':
                    print("national team of" + parts[1])
                else:
                    card = get_card(int(parts[1]))

                    if card:
                        print(
                            f"#{card[0]} | "
                            f"{card[1]} | "
                            f"{card[2]} | "
                            f"qty={card[3] or 0}"
                        )
                    else:
                        print("Nie znaleziono.")

            case "duplicates":
                duplicates = get_duplicates()

                if not duplicates:
                    print("Brak duplikatów.")
                    continue

                for card in duplicates:
                    print(
                        f"{card[0]} | {card[1]} | "
                        f"sztuk: {card[2]-1}"
                    )

            case "missing":
                missing = get_missing()

                for card in missing:
                    print(f"{card[0]} | {card[1]} | {card[2]}")

            case "stats":
                stats = get_stats()

                print(f"Posiadane: {stats['owned']}")
                print(f"Brakujące: {stats['missing']}")
                print(f"Ukończenie: {stats['percentage']}%")
                print(f"Wszystkich kart: {stats['all cards']}")

            case "help":
                print_help()

            case "exit":
                break

            case _:
                print("Nieznana komenda.")


if __name__ == "__main__":
    main()