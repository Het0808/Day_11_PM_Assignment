import logging

# log errors to file, show clean messages on screen
logging.basicConfig(
    filename="age_calculator.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_age_from_user():
    while True:
        try:
            raw = input("Enter your age: ").strip()
            
            if not raw:
                raise ValueError("You didn't enter anything.")
            
            age = int(raw)
            
            if age < 0 or age > 150:
                raise ValueError(f"Age {age} is not realistic. Must be between 0 and 150.")
        
        except ValueError as e:
            logging.error("Bad age input: %s", e)
            print(f"  Oops — {e} Please try again.\n")
        
        else:
            # only runs if no exception was raised
            print(f"\nIn 10 years you'll be {age + 10}.")
            print(f"In 20 years you'll be {age + 20}.")
            break
        
        finally:
            # always runs — useful for cleanup or debug markers
            # here just a dev note in the log, not shown to user
            logging.debug("get_age_from_user loop iteration complete.")


if __name__ == "__main__":
    print("=== Age Calculator ===\n")
    get_age_from_user()
