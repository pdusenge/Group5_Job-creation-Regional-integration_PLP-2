"""
Regional E-commerce Platform

Main entry point for the application.
"""
import os
import sys
from datetime import datetime

from config import APP_NAME, APP_VERSION
from database import get_session, init_db, UserRole, Business, OrderStatus
import auth
import products
import orders
import helper


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    """Pause execution until user presses Enter."""
    input("\nPress Enter to continue...")


def get_input(prompt, required=False, input_type=str):
    """
    Get validated input from the user.

    Args:
        prompt (str): Prompt message to display
        required (bool, optional): Whether input is required. Defaults to False.
        input_type (type, optional): Type to convert input to. Defaults to str.

    Returns:
        Any: The validated input converted to input_type, or None if not required and empty
    """
    while True:
        value = input(prompt)

        if not value:
            if required:
                print("This field is required.")
                continue
            return None

        try:
            return input_type(value)
        except ValueError:
            print(f"Invalid input. Expected {input_type.__name__}.")


def get_int(prompt, required=False, min_value=None, max_value=None):
    """
    Get an integer input from the user.

    Args:
        prompt (str): Prompt message to display
        required (bool, optional): Whether input is required. Defaults to False.
        min_value (int, optional): Minimum allowed value. Defaults to None.
        max_value (int, optional): Maximum allowed value. Defaults to None.

    Returns:
        int: The validated integer input, or None if not required and empty
    """
    while True:
        value = input(prompt)

        if not value:
            if required:
                print("This field is required.")
                continue
            return None

        try:
            int_value = int(value)

            if min_value is not None and int_value < min_value:
                print(f"Value must be at least {min_value}.")
                continue

            if max_value is not None and int_value > max_value:
                print(f"Value must be at most {max_value}.")
                continue

            return int_value

        except ValueError:
            print("Invalid input. Expected an integer.")


def get_float(prompt, required=False, min_value=None, max_value=None):
    """
    Get a float input from the user.

    Args:
        prompt (str): Prompt message to display
        required (bool, optional): Whether input is required. Defaults to False.
        min_value (float, optional): Minimum allowed value. Defaults to None.
        max_value (float, optional): Maximum allowed value. Defaults to None.

    Returns:
        float: The validated float input, or None if not required and empty
    """
    while True:
        value = input(prompt)

        if not value:
            if required:
                print("This field is required.")
                continue
            return None

        try:
            float_value = float(value)

            if min_value is not None and float_value < min_value:
                print(f"Value must be at least {min_value}.")
                continue

            if max_value is not None and float_value > max_value:
                print(f"Value must be at most {max_value}.")
                continue

            return float_value

        except ValueError:
            print("Invalid input. Expected a number.")

def show_menu(title, options):
    """
    Display a menu with options and get user choice.
    
    Args:
        title (str): Menu title
        options (list): List of option strings
        
    Returns:
        int: Selected option index (0-based) or -1 to exit
    """
    print(f"\n--- {title} ---")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Back/Exit")
    
    max_option = len(options)
    choice = get_int("\nEnter your choice (0-{0}): ".format(max_option), required=True, min_value=0, max_value=max_option)
    return choice - 1 if choice > 0 else -1

def setup_database():
    """Set up the database and create necessary tables."""
    try:
        # Check if MySQL server is running
        from database import engine
        conn = engine.connect()
        conn.close()

        # Initialize database
        init_db()
        print("Database setup completed successfully.")
    except Exception as e:
        print(f"Database setup failed: {str(e)}")
        print("\nMake sure MySQL is running and the database credentials in config.py are correct.")
        sys.exit(1)


def main_menu():
    """Display the main menu."""
    while True:
        clear_screen()
        print(f"\n=== {APP_NAME} v{APP_VERSION} ===")
        print(f"Current Date: {datetime.now().strftime('%Y-%m-%d')}")

        options = [
            "Browse Products",
            "Search Products",
            "Register",
            "Login"
        ]

        choice = show_menu("Main Menu", options)

        if choice == -1:  # Exit application
            print("\nThank you for using the Regional E-commerce Platform!")
            break


if __name__ == "__main__":
    try:
        setup_database()
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting application...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
    finally:
        from database import close_session
        close_session()
