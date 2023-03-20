import psycopg2 as p

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE clients(
        client_id SERIAL PRIMARY KEY,
        name VARCHAR(40) NOT NULL,
        last_name VARCHAR(60) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL
        );""")
        conn.commit()
        cur.execute("""
        CREATE TABLE phones(
        phone_id SERIAL PRIMARY KEY,
        phone_number VARCHAR(100) UNIQUE NOT NULL,
        client_id INTEGER REFERENCES clients(client_id) ON DELETE CASCADE
        );
        """)

def add_client(conn, name, last_name, email, phones=[]):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO clients(name, last_name, email) VALUES (%s, %s, %s);""", (name, last_name, email))
        conn.commit()
        cur.execute("""SELECT client_id FROM clients WHERE name = %s""", (name,))
        client_id = cur.fetchone()[0]
        for phone_number in phones:
            cur.execute("""INSERT INTO phones (phone_number, client_id) VALUES (%s, %s);""", (phone_number, client_id))
        conn.commit()

def add_phone(conn, client_id, phone_number):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO phones (phone_number, client_id) VALUES (%s, %s);""", (phone_number, client_id))
        conn.commit()

def change_client(conn, client_id, name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        request = "UPDATE clients SET "
        values = []
        if name:
            request += "name = %s,"
            values.append(name)
        if last_name:
            request += "last_name = %s,"
            values.append(last_name)
        if email:
            request += "email = %s,"
            values.append(email)
        if phones:
            cur.execute("""DELETE FROM phones WHERE client_id = %s;""", (client_id,))
            for phone in phones:
                cur.execute("""INSERT INTO phones (phone_number, client_id) VALUES (%s, %s);""", (phone, client_id))

        request = request.rstrip(',') + "WHERE client_id = %s"
        values.append(client_id)
        cur.execute(request, tuple(values))
        conn.commit()

def delete_phone(conn, phone):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM phones WHERE phone_number = %s;""", (phone,))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM clients WHERE client_id = %s;""", (client_id,))
        conn.commit()

def find_client(conn, name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if name:
            cur.execute("""
            SELECT c.client_id, c.last_name, c.email, phones.phone_number FROM clients c
            JOIN phones ON c.client_id = phones.client_id
            WHERE name = %s;
            """, (name,))
        elif last_name:
            cur.execute("""
                        SELECT c.client_id, c.name, c.email, phones.phone_number FROM clients c
                        JOIN phones ON c.client_id = phones.client_id
                        WHERE last_name = %s;
                        """, (last_name,))
        elif email:
            cur.execute("""
                        SELECT c.client_id, c.name, c.last_name, phones.phone_number FROM clients c 
                        JOIN phones ON c.client_id = phones.client_id
                        WHERE email = %s;
                        """, (email,))
        elif phone:
            cur.execute("""
            SELECT c.client_id, c.name, c.last_name, c.email FROM phones p
            JOIN clients c on p.client_id = c.client_id
            WHERE phone_number = %s;
            """, (phone,))
        print(cur.fetchone())

def select_all(conn):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT * FROM clients c
        JOIN phones p ON c.client_id = p.client_id;
        """)
        print(cur.fetchall())

with p.connect(database="art", user="postgres", password="qwerty") as conn:
    create_db(conn)
    add_client(conn, 'Snoop', 'Dogg', 'SG@gmail.com', ['+9173335522'])
    add_client(conn, 'Ozzy', 'Ozzborn', 'ozzy@gmail.com', ['+9871345667', '+9871345668'])
    add_client(conn, 'Marilyn', 'Manson', 'mm@yahoo.com', ['+9172343466'])
    select_all(conn)
    print('\n')
    change_client(conn, 3, 0, 'Ronaldo')
    find_client(conn, 'Marilyn')
    select_all(conn)
    print('\n')
    delete_phone(conn, '+9173335522')
    delete_client(conn, 3)
    select_all(conn)

conn.close()