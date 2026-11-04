from gearshare import GearShare


def show_menu():
    print("\n" + "=" * 45)
    print("          GEARSHARE RENTAL SYSTEM")
    print("=" * 45)
    print("1. View catalogue")
    print("2. View customers")
    print("3. Rent an item")
    print("4. Return an item")
    print("5. View customer report")
    print("6. View overdue rentals")
    print("7. View audit log")
    print("0. Exit")
    print("=" * 45)


def main():
    app = GearShare(db_path="gearshare.db")

    while True:
        show_menu()

        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                for item in app.catalogue():
                    print(item, "| Type:", type(item).__name__)

            elif choice == "2":
                for customer in app.customers.values():
                    print(customer)

            elif choice == "3":
                customer_id = input("Customer ID: ").strip()
                sku = input("SKU: ").strip()

                rental = app.rent_item(customer_id, sku)
                print("Rental successful!")
                print(rental)

            elif choice == "4":
                rental_id = input("Rental ID: ").strip()

                result = app.return_item(rental_id)
                print("Return successful!")
                print(result)

            elif choice == "5":
                customer_id = input("Customer ID: ").strip()

                print(app.customer_report(customer_id))

            elif choice == "6":
                overdue = list(app.overdue_rentals())

                if not overdue:
                    print("No overdue rentals.")

                for rental in overdue:
                    print(
                        rental,
                        "| Late days:",
                        rental.days_late(app.today)
                    )

            elif choice == "7":
                for entry in app.audit_log:
                    print(entry)

            elif choice == "0":
                print("Thank you for using GearShare!")
                break

            else:
                print("Invalid choice.")

        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()