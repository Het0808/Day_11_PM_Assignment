import logging

logging.basicConfig(
    filename="shopping_list.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# custom exception - makes errors more meaningful than plain ValueError
class EmptyItemError(Exception):
    """Raised when user tries to add a blank item to the list."""
    pass

class DuplicateItemError(Exception):
    """Raised when item already exists in the shopping list."""
    pass


def add_item(shopping_list, item_name):
    """
    Add an item to the shopping list.
    Raises EmptyItemError or DuplicateItemError on bad input.
    """
    item_name = item_name.strip()
    
    if not item_name:
        raise EmptyItemError("Item name cannot be empty.")
    
    if item_name.lower() in [i.lower() for i in shopping_list]:
        raise DuplicateItemError(f"'{item_name}' is already in your list.")
    
    shopping_list.append(item_name)
    return shopping_list


def remove_item(shopping_list, index_str):
    """
    Remove item by number (1-based, as shown to user).
    Raises ValueError or IndexError on bad input.
    """
    index = int(index_str)  # ValueError if not a number
    
    if index < 1 or index > len(shopping_list):
        raise IndexError(f"No item #{index}. List only has {len(shopping_list)} items.")
    
    removed = shopping_list.pop(index - 1)
    return removed


def show_list(shopping_list):
    if not shopping_list:
        print("  (list is empty)")
        return
    for i, item in enumerate(shopping_list, 1):
        print(f"  {i}. {item}")


def main():
    shopping_list = []
    
    print("=== Shopping List Manager ===")
    print("Commands: add, remove, show, quit\n")
    
    while True:
        try:
            command = input("Command: ").strip().lower()
            
            if command == "quit":
                break
            
            elif command == "add":
                item = input("  Item name: ")
                add_item(shopping_list, item)
                print(f"  Added! List now has {len(shopping_list)} item(s).\n")
            
            elif command == "remove":
                show_list(shopping_list)
                if not shopping_list:
                    print("  Nothing to remove.\n")
                    continue
                num = input("  Remove item #: ")
                removed = remove_item(shopping_list, num)
                print(f"  Removed '{removed}'.\n")
            
            elif command == "show":
                show_list(shopping_list)
                print()
            
            else:
                print("  Unknown command. Try: add, remove, show, quit\n")
        
        except EmptyItemError as e:
            logging.warning("Empty item attempt: %s", e)
            print(f"  Can't do that: {e}\n")
        
        except DuplicateItemError as e:
            logging.warning("Duplicate item attempt: %s", e)
            print(f"  Already there: {e}\n")
        
        except ValueError:
            logging.warning("Non-numeric input when removing item.")
            print("  Please enter a number for the item to remove.\n")
        
        except IndexError as e:
            logging.warning("Out of range remove attempt: %s", e)
            print(f"  Invalid selection: {e}\n")
    
    print("\nFinal list:")
    show_list(shopping_list)
    print("Bye!")


if __name__ == "__main__":
    main()
