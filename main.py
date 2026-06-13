from database import (
    initialize_database,
    add_card,
    remove_card,
    get_card,
    get_duplicates,
    get_stats,
    get_missing,
    get_cards_by_country,
    get_country_stats,
    get_owned_cards,
    special
)


def print_help():
    print("""
Komendy:

add <nr>
remove <nr>

show owned
show <nr>
show (NAT) - nationality 3 letters

duplicates
missing
stats

exit
""")


def print_card(card, duplicate=False):
    if duplicate:
        print(f"{card[0]:<3} | {card[1]:<24} | {card[2]:<18} | sztuk={card[3]-1}")
    else:
        print(f"{card[0]:<3} | {card[1]:<24} | {card[2]:<18} | sztuk={card[3] or 0}")


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
                new_cards = []
                duplicate_cards = []
                for num in parts[1:]:
                    card_number = int(num)
                    is_new = add_card(card_number)
                    card = get_card(card_number)
                    if is_new:
                        new_cards.append(card)
                    else:
                        duplicate_cards.append(card)

                if new_cards:
                    print(f"Dodano: {len(new_cards)} nowych kart")
                    for card in new_cards:
                        print(f"  {card[0]:<4} | {card[1]}")
                else:
                    print("Żadna karta nie była nowa.")
                print(f"Dodano: {len(duplicate_cards)} duplikatów")
                for card in duplicate_cards:
                    print_card(card)

            case "remove":
                for num in parts[1:]:
                    remove_card(int(num))

                print("Usunięto.")

            case "show":
                if parts[1] == "owned":
                    cards = get_owned_cards()
                    for card in enumerate(cards):
                        print_card(card)

                elif parts[1].isnumeric():
                    for num in parts[1:]:
                        card = get_card(int(num))
                        if card:
                            print_card(card)
                        else:
                            print(f"#{num} — nie znaleziono.")

                else:
                    arg = " ".join(parts[1:])
                    cards = get_cards_by_country(arg)
                    stats = get_country_stats(arg)
                    if cards == 0:
                        print("wrong code/country")
                    else:
                        print(f"Posiadane: {stats['owned']}")
                        print(f"Brakujące: {stats['missing']}")
                        print(f"Ukończenie: {stats['percentage']}%")
                        print(f"Wszystkich kart: {stats['total']}")

                        for i, card in enumerate(cards):
                            label = special.get(i, "")
                            suffix = f" [{label}]" if label else ""
                            qty = card[2] or 0
                            name_with_suffix = f"{card[1]}{suffix}"
                            print(f"{card[0]:<4} | {name_with_suffix:<28} | sztuk={qty}")

            case "duplicates":
                duplicates = get_duplicates()

                if not duplicates:
                    print("Brak duplikatów.")
                    continue

                for card in duplicates:
                    print_card(card, duplicate=True)

            case "missing":
                missing = get_missing()

                for card in missing:
                    print_card(card)

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