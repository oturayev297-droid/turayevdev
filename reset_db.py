import psycopg
import sys

def force_reset():
    passwords_to_try = ['', 'postgres', '12345678', 'admin', 'root']
    success = False
    
    print("--- 🐘 Automated Password Reset Attempt ---")
    
    for pwd in passwords_to_try:
        try:
            print(f"Trying to connect as 'postgres' with password: '{pwd}'...")
            conn = psycopg.connect(
                dbname='postgres',
                user='postgres',
                password=pwd,
                host='127.0.0.1',
                autocommit=True,
                connect_timeout=2
            )
            print(f"✅ SUCCESS: Logged in as admin!")
            
            with conn.cursor() as cur:
                # Reset master password
                print("Setting password for user 'master'...")
                cur.execute("ALTER USER master WITH PASSWORD 'ozodbek12345678';")
                
                # Ensure database exists
                print("Ensuring database 'portfolio' exists...")
                cur.execute("SELECT 1 FROM pg_database WHERE datname='portfolio'")
                if not cur.fetchone():
                    cur.execute("CREATE DATABASE portfolio")
                    print("✅ Database 'portfolio' created.")
                else:
                    print("✅ Database 'portfolio' already exists.")
            
            conn.close()
            success = True
            break
        except Exception as e:
            print(f"❌ Failed with password '{pwd}': {str(e).splitlines()[0]}")
    
    if success:
        print("\n🎉 ALL GOOD! Now run 'python manage.py migrate'")
    else:
        print("\n⚠️ Auto-reset failed. Please use pgAdmin GUI to reset the password for 'master'.")

if __name__ == "__main__":
    force_reset()
