import sys
from memory.memory_manager import MemoryManager

def main():
    manager = MemoryManager(None) # Brain is not needed for CRUD
    
    while True:
        print("\n--- REETA Memory Manager ---")
        print("1. List Facts")
        print("2. Delete Fact")
        print("3. View User Profile")
        print("4. Set User Profile Key")
        print("5. Exit")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            memories = manager.list_memories()
            for m in memories:
                print(f"[{m['id']}] ({m['category']}) {m['content']}")
        elif choice == '2':
            mem_id = input("Enter ID to delete: ")
            try:
                if manager.delete_memory(int(mem_id)):
                    print("Deleted.")
                else:
                    print("Not found.")
            except ValueError:
                print("Invalid ID.")
        elif choice == '3':
            profile = manager.get_user_profile()
            for k, v in profile.items():
                print(f"{k}: {v}")
        elif choice == '4':
            k = input("Key: ")
            v = input("Value: ")
            manager.set_user_profile(k, v)
            print("Set.")
        elif choice == '5':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
