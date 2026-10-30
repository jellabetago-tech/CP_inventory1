import os
import mysql.connector
from mysql.connector import Error

# XAMPP defaults to MySQL on localhost:3306 with a root account that has no
# password unless one was configured manually.
db_config = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'cp_shop_pos')
}

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        connection = mysql.connector.connect(**db_config, use_pure=True)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"\n[Error] Database connection failed: {e}")
        return None

# ==========================================
# 1. CREATE OPERATION (Add New Phone)
# ==========================================
def create_phone_record():
    print("\n--- ADD NEW PHONE TO INVENTORY ---")
    brand = input("Enter Brand: ").strip()
    if not brand:
        print("[Error] Brand cannot be empty.")
        return

    model = input("Enter Model Name: ").strip()
    if not model:
        print("[Error] Model Name cannot be empty.")
        return

    # Input Validation: IMEI must be exactly 15 digits long
    imei = input("Enter 15-digit IMEI Number: ").strip()
    if not (imei.isdigit() and len(imei) == 15):
        print("[Error] Invalid IMEI. It must be exactly 15 numeric digits.")
        return

    # Input Validation: Price must be a valid float/integer
    try:
        price = float(input("Enter Selling Price: "))
        if price <= 0:
            print("[Error] Price must be greater than 0.")
            return
    except ValueError:
        print("[Error] Invalid input. Price must be a number.")
        return

    connection = get_db_connection()
    if connection is None:
        return

    cursor = None
    try:
        cursor = connection.cursor()
        # Parameterized query to prevent SQL Injection
        query = """INSERT INTO phone_inventory (brand, model_name, imei, price) 
                   VALUES (%s, %s, %s, %s)"""
        values = (brand, model, imei, price)
        
        cursor.execute(query, values)
        connection.commit()
        print(f"\n[SUCCESS] Added successfully! Internal ID: {cursor.lastrowid}")
    except mysql.connector.IntegrityError:
        print("\n[Error] Duplicate Entry! A phone with this IMEI already exists in the system.")
    except Error as e:
        print(f"\n[Error] Failed to insert record: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

# ==========================================
# 2. READ OPERATION (Display Records)
# ==========================================
def read_phone_records():
    print("\n--- CELL PHONE STOCK LIST ---")
    connection = get_db_connection()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        query = "SELECT id, brand, model_name, imei, price, status FROM phone_inventory"
        cursor.execute(query)
        records = cursor.fetchall()

        if not records:
            print("No stock records found in the database.")
            return

        # Printing records cleanly in a text table format
        print(f"{'ID':<5} | {'Brand':<12} | {'Model':<20} | {'IMEI':<16} | {'Price':<12} | {'Status':<10}")
        print("-" * 75)
        for row in records:
            print(f"{row[0]:<5} | {row[1]:<12} | {row[2]:<20} | {row[3]:<16} | {row[4]:<12,.2f} | {row[5]:<10}")
            
    except Error as e:
        print(f"\n[Error] Failed to retrieve data: {e}")
    finally:
        cursor.close()
        connection.close()

# ==========================================
# 3. UPDATE OPERATION (Modify Price or Status)
# ==========================================
def update_phone_record():
    print("\n--- UPDATE PHONE DETAILS / MARK AS SOLD ---")
    try:
        phone_id = int(input("Enter the Internal Phone ID to update: "))
    except ValueError:
        print("[Error] ID must be a numeric integer.")
        return

    connection = get_db_connection()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        # Verify if the item exists first
        check_query = "SELECT id, brand, model_name, price, status FROM phone_inventory WHERE id = %s"
        cursor.execute(check_query, (phone_id,))
        record = cursor.fetchone()

        if not record:
            print(f"[Error] No phone item found with ID {phone_id}.")
            return

        print(f"\nFound Item: {record[1]} {record[2]} | Current Price: {record[3]:,.2f} | Status: {record[4]}")
        print("1. Update Price")
        print("2. Change Status (Available / Sold)")
        print("3. Cancel Update")
        
        choice = input("Select update action (1-3): ").strip()

        if choice == '1':
            try:
                new_price = float(input("Enter new selling price: "))
                if new_price <= 0:
                    print("[Error] Price must be greater than 0.")
                    return
                update_query = "UPDATE phone_inventory SET price = %s WHERE id = %s"
                cursor.execute(update_query, (new_price, phone_id))
                connection.commit()
                print("\n[Success] Item price updated successfully.")
            except ValueError:
                print("[Error] Price must be a valid number.")
                
        elif choice == '2':
            print("1. Mark as Available")
            print("2. Mark as Sold")
            status_choice = input("Select choice (1-2): ").strip()
            new_status = 'Available' if status_choice == '1' else 'Sold' if status_choice == '2' else None
            
            if new_status:
                update_query = "UPDATE phone_inventory SET status = %s WHERE id = %s"
                cursor.execute(update_query, (new_status, phone_id))
                connection.commit()
                print(f"\n[Success] Status changed successfully to '{new_status}'.")
            else:
                print("[Error] Invalid status selection option.")
                
        elif choice == '3':
            print("Update operation canceled.")
        else:
            print("[Error] Invalid choice.")

    except Error as e:
        print(f"\n[Error] Update failed: {e}")
    finally:
        cursor.close()
        connection.close()

# ==========================================
# 4. DELETE OPERATION (Remove Record)
# ==========================================
def delete_phone_record():
    print("\n--- DELETE PHONE RECORD ---")
    try:
        phone_id = int(input("Enter the Phone ID to delete: "))
    except ValueError:
        print("[Error] ID must be a numeric integer.")
        return

    connection = get_db_connection()
    if connection is None:
        return

    try:
        cursor = connection.cursor()
        # Verify item exists
        check_query = "SELECT brand, model_name, imei FROM phone_inventory WHERE id = %s"
        cursor.execute(check_query, (phone_id,))
        record = cursor.fetchone()

        if not record:
            print(f"[Error] Record with ID {phone_id} does not exist.")
            return

        # Double confirmation check requirement from image guidelines
        print(f"\n⚠️ WARNING: You are about to permanently delete: {record[0]} {record[1]} (IMEI: {record[2]})")
        confirm = input("Type 'YES' to confirm deletion: ").strip()

        if confirm == 'YES':
            delete_query = "DELETE FROM phone_inventory WHERE id = %s"
            cursor.execute(delete_query, (phone_id,))
            connection.commit()
            print("\n[Success] Record wiped from database permanently.")
        else:
            print("\nDeletion canceled. Safety mechanism preserved the record.")

    except Error as e:
        print(f"\n[Error] Action blocked: {e}")
    finally:
        cursor.close()
        connection.close()

# ==========================================
# MENU INTERFACE LOOP
# ==========================================
def main_menu():
    while True:
        print("\n=========================================")
        print("       CELLPHONE SHOP POS SYSTEM         ")
        print("=========================================")
        print("[1] Create - Add New Phone Stock")
        print("[2] Read   - View Phone Inventory & Sales")
        print("[3] Update - Edit Price or Sales Status")
        print("[4] Delete - Remove Bad Records")
        print("[5] Exit Application")
        print("=========================================")
        
        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            create_phone_record()
        elif choice == '2':
            read_phone_records()
        elif choice == '3':
            update_phone_record()
        elif choice == '4':
            delete_phone_record()
        elif choice == '5':
            print("\nClosing open MySQL links... System down. Goodbye!")
            break
        else:
            print("\n[Invalid Selection] Please choose a digit from 1 to 5.")

if __name__ == "__main__":
    main_menu()