from pymongo import MongoClient
from getpass import getpass

uri = getpass("Enter Mongo URI: ")
client = MongoClient(uri)
db = client["cat_db"]
cats = db["cats"]

# Додамо початкового кота, якщо БД порожня
if cats.count_documents({}) == 0:
    cats.insert_one({
        "name": "barsik",
        "age": 3,
        "features": ["ходить в капці", "дає себе гладити", "рудий"]
    })

# Створення кота за шаблоном
def create_cat():
    name = input("Please enter a name: ")
    try:
        age = int(input("Please enter age: "))
    except ValueError:
        print("Age must be a number.")
        return

    features = []
    while True:
        add_feat = input(f"Does {name} have any features? [Y/n]: ").strip().lower()
        if add_feat == 'n':
            break
        feature = input("Enter the feature: ")
        features.append(feature)

    print(f'\nDo you want to add: \n"name": "{name}", \n"age": {age}, \n"features": {features} \nto your DB? [Y/n]')
    confirm = input().strip().lower()
    if confirm == 'y':
        cats.insert_one({"name": name, "age": age, "features": features})
        print("Cat's info successfully added.\n")

# Читання запису з БД за імʼям, або всіх записів, якщо імʼя порожнє
def read_cats():
    name_filter = input("\nEnter cat name to search (or press Enter to show all): ").strip()
    query = {"name": name_filter} if name_filter else {}
    results = list(cats.find(query))

    if not results:
        print("No cats found.\n")
        return

    print("\nCats in DB:")
    for cat in results:
        features = ", ".join(cat.get("features", []))
        print(f'{cat["_id"]}: {cat["name"]}, {cat["age"]} years old, features: {features}')
    print()

# Оновлення полів записів
def update_cat():
    cat_name = input("Enter the name of the cat you want to update: ")
    try:
        cat = cats.find_one({"name": cat_name})
        if not cat:
            print("Cat not found.")
            return
    except:
        print("Invalid ID format.")
        return

    field = input("What do you want to update? ( (n)ame, (a)ge, (f)eatures) [n/a/f]: ").strip().lower()

    if field == "n":
        new_name = input("Enter new name: ").strip()
        cats.update_one({"name": cat_name}, {"$set": {"name": new_name}})
    elif field == "a":
        try:
            new_age = int(input("Enter new age: ").strip())
            cats.update_one({"name": cat_name}, {"$set": {"age": new_age}})
        except ValueError:
            print("Age must be a number.")
            return
    elif field == "f":
        modify = input("Do you want to (a)dd to existing features, (d)elete them, or (k)eep as is? [a/d/k]: ").strip().lower()
        if modify == 'a':
            features = []
            while True:
                feature = input("Enter feature (or press Enter to finish): ").strip()
                if not feature:
                    break
                features.append(feature)
            if features:
                cats.update_one({"name": cat_name}, {"$push": {"features": {"$each": features}}})
        elif modify == 'd':
            current_features = cat.get("features", [])
            print(f"Current features: {', '.join(current_features) if current_features else 'No features listed.'}")

            features_to_remove = []
            while True:
                feature = input("Type a feature you want to delete (or press Enter to finish): ").strip()
                if not feature:
                    break
                if feature in current_features:
                    features_to_remove.append(feature)
                else:
                    print(f'"{feature}" not found in current features.')

            updated_features = [f for f in current_features if f not in features_to_remove]
            cats.update_one({"name": cat_name}, {"$set": {"features": updated_features}})
            print("Features successfully updated.")
        elif modify == 'k':
            print("Features unchanged.")
            return
        else:
            print("Unknown option. Features unchanged.")
            return
    else:
        print("Unknown field.")
        return

    print("Cat successfully updated.\n")

# Видалення запису за імʼям, або всіх записів, якщо імʼя ппорожнє
def delete_cat():
    cat_name = input("Enter the name of the cat you want to delete (or press Enter to delete all): ")
    try:
        if not cat_name:
            agreement = input("Confirm that you want to delete all records[Y/n]: ").strip().lower()
            if agreement == 'y':
                cats.drop()
                print("All cats deleted.\n")
                return
            elif agreement == 'n':
                print('The cats thank you for saving them')
                return
        result = cats.delete_one({"name": cat_name})
        if result.deleted_count == 1:
            print("Cat successfully deleted.\n")
        else:
            print("Cat not found.\n")
    except:
        print("Invalid name.\n")


def main():
    print("\nAvailable commands:\ncreate - Add a new cat\nread - Show all cats\nupdate - Update cat info\ndelete - Delete a cat by ID\nexit - Exit the program\n")
    while True:
        cmd = input(">>> ").strip().lower()

        if cmd == "create":
            create_cat()
        elif cmd == "read":
            read_cats()
        elif cmd == "update":
            update_cat()
        elif cmd == "delete":
            delete_cat()
        elif cmd == "exit":
            print("Bye!")
            break
        else:
            print("Unknown command.\n")


if __name__ == "__main__":
    main()
