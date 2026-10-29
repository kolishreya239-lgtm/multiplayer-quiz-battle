from models import db
from models.user import User, PlayerStats, Achievement, UserAchievement
from models.question import Category, Question
from models.game import MatchHistory, MatchParticipant
from datetime import datetime, timezone, timedelta

def seed_database(app):
    with app.app_context():
        # Check if already seeded
        if Category.query.first():
            return

        print("[Seed] Populating initial categories, questions, achievements, and demo users...")

        # 1. Create Achievements
        achievements_data = [
            {'code': 'first_win', 'title': 'First Blood', 'description': 'Win your very first quiz battle!', 'icon': 'award', 'xp_points': 100},
            {'code': 'quiz_master', 'title': 'Quiz Master', 'description': 'Achieve 5 battle victories!', 'icon': 'crown', 'xp_points': 300},
            {'code': 'hot_streak', 'title': 'On Fire', 'description': 'Hit a 4+ answer streak in a single match!', 'icon': 'flame', 'xp_points': 200},
            {'code': 'speed_demon', 'title': 'Speed Demon', 'description': 'Average under 3 seconds response with high accuracy!', 'icon': 'zap', 'xp_points': 250},
            {'code': 'perfect_round', 'title': 'Flawless Victory', 'description': 'Score 100% correct answers in a full match!', 'icon': 'shield', 'xp_points': 500},
        ]
        created_achievements = {}
        for ach in achievements_data:
            a = Achievement(**ach)
            db.session.add(a)
            created_achievements[ach['code']] = a
        db.session.flush()

        # 2. Create Categories
        categories_data = [
            {
                'name': 'Python Programming',
                'slug': 'python-programming',
                'description': 'Data structures, OOP, decorators, generators, and standard library.',
                'icon_name': 'code',
                'color_hex': '#38BDF8'
            },
            {
                'name': 'Computer Science',
                'slug': 'computer-science',
                'description': 'Algorithms, data structures, OS, networking, and memory architectures.',
                'icon_name': 'cpu',
                'color_hex': '#A855F7'
            },
            {
                'name': 'Web Development',
                'slug': 'web-development',
                'description': 'HTTP, JavaScript, HTML5/CSS3, frameworks, APIs, and modern frontend.',
                'icon_name': 'globe',
                'color_hex': '#22C55E'
            },
            {
                'name': 'Cybersecurity',
                'slug': 'cybersecurity',
                'description': 'Cryptography, web exploits, penetration testing, networks, and defense.',
                'icon_name': 'shield-alert',
                'color_hex': '#F43F5E'
            },
            {
                'name': 'General Knowledge',
                'slug': 'general-knowledge',
                'description': 'World history, geography, arts, discoveries, and monumental events.',
                'icon_name': 'book-open',
                'color_hex': '#EAB308'
            },
            {
                'name': 'Science & Technology',
                'slug': 'science-technology',
                'description': 'Physics, quantum mechanics, artificial intelligence, and space exploration.',
                'icon_name': 'atom',
                'color_hex': '#06B6D4'
            },
            {
                'name': 'Mathematics & Logic',
                'slug': 'mathematics-logic',
                'description': 'Discrete math, probability, combinatorics, and brain-bending logical puzzles.',
                'icon_name': 'binary',
                'color_hex': '#EC4899'
            },
            {
                'name': 'Gaming & Pop Culture',
                'slug': 'gaming-pop-culture',
                'description': 'Classic games, esports tournaments, retro consoles, and gaming lore.',
                'icon_name': 'gamepad-2',
                'color_hex': '#10B981'
            }
        ]

        cat_objs = {}
        for c in categories_data:
            cat = Category(**c)
            db.session.add(cat)
            cat_objs[c['slug']] = cat
        db.session.flush()

        # 3. Create Questions (15 per category = 120 questions)
        raw_questions = [
            # --- Python Programming ---
            {
                'cat': 'python-programming', 'diff': 'easy',
                'q': 'What is the output of bool([]) in Python?',
                'a': 'True', 'b': 'False', 'c': 'None', 'd': 'IndexError',
                'ans': 'B', 'exp': 'In Python, empty collections like empty lists, dicts, and tuples evaluate to False in a boolean context.'
            },
            {
                'cat': 'python-programming', 'diff': 'easy',
                'q': 'Which keyword is used to define an anonymous inline function in Python?',
                'a': 'def', 'b': 'func', 'c': 'lambda', 'd': 'anon',
                'ans': 'C', 'exp': 'The "lambda" keyword is used to create small, one-line anonymous functions in Python.'
            },
            {
                'cat': 'python-programming', 'diff': 'easy',
                'q': 'Which data structure is immutable in Python?',
                'a': 'List', 'b': 'Dictionary', 'c': 'Tuple', 'd': 'Set',
                'ans': 'C', 'exp': 'Tuples cannot be modified after creation, making them immutable.'
            },
            {
                'cat': 'python-programming', 'diff': 'medium',
                'q': 'What does the "is" operator check in Python?',
                'a': 'Value equality', 'b': 'Object identity in memory', 'c': 'Data type match', 'd': 'Hash equality',
                'ans': 'B', 'exp': 'The "is" operator compares whether two variables point to the exact same object in memory (id(a) == id(b)).'
            },
            {
                'cat': 'python-programming', 'diff': 'medium',
                'q': 'Which built-in Python function returns an iterator of tuples containing item index and value?',
                'a': 'zip()', 'b': 'map()', 'c': 'enumerate()', 'd': 'range()',
                'ans': 'C', 'exp': 'enumerate() adds a counter to an iterable and returns it as an enumerate object of (index, value) tuples.'
            },
            {
                'cat': 'python-programming', 'diff': 'medium',
                'q': 'What keyword turns a regular Python function into a generator?',
                'a': 'return', 'b': 'yield', 'c': 'async', 'd': 'next',
                'ans': 'B', 'exp': 'When a function contains the "yield" keyword, executing it returns a generator iterator.'
            },
            {
                'cat': 'python-programming', 'diff': 'medium',
                'q': 'What will [x**2 for x in range(4)] produce in Python?',
                'a': '[1, 4, 9, 16]', 'b': '[0, 1, 4, 9]', 'c': '[0, 1, 2, 3]', 'd': '[0, 2, 4, 6]',
                'ans': 'B', 'exp': 'range(4) produces 0, 1, 2, 3. Squaring each yields 0, 1, 4, and 9.'
            },
            {
                'cat': 'python-programming', 'diff': 'hard',
                'q': 'What is the purpose of the Python Global Interpreter Lock (GIL)?',
                'a': 'To prevent memory leaks', 'b': 'To ensure only one thread executes Python bytecode at a time in CPython', 'c': 'To encrypt socket data', 'd': 'To speed up multi-core matrix math',
                'ans': 'B', 'exp': 'The GIL is a mutex in CPython that protects memory management by preventing multiple native threads from executing Python bytecodes concurrently.'
            },
            {
                'cat': 'python-programming', 'diff': 'hard',
                'q': 'In Python, what does the __slots__ declaration inside a class do?',
                'a': 'Allows multiple inheritance', 'b': 'Prevents creation of an instance __dict__ to optimize memory usage', 'c': 'Makes all attributes private', 'd': 'Enforces static typing',
                'ans': 'B', 'exp': '__slots__ reserves space for a fixed set of attributes, avoiding the creation of __dict__ per instance and saving significant memory.'
            },
            {
                'cat': 'python-programming', 'diff': 'hard',
                'q': 'What is the Method Resolution Order (MRO) algorithm used in Python 3?',
                'a': 'Depth-First Search', 'b': 'C3 Linearization', 'c': 'Breadth-First Search', 'd': 'Dijkstra MRO',
                'ans': 'B', 'exp': 'Python uses the C3 Linearization algorithm to determine class inheritance hierarchy and attribute lookup order.'
            },
            {
                'cat': 'python-programming', 'diff': 'easy',
                'q': 'Which method is called when an object is converted to string for users?',
                'a': '__repr__', 'b': '__str__', 'c': '__init__', 'd': '__len__',
                'ans': 'B', 'exp': '__str__ is intended to return a readable string representation of an object.'
            },
            {
                'cat': 'python-programming', 'diff': 'medium',
                'q': 'What module in Python provides tools for working with high-performance collections like deque and Counter?',
                'a': 'itertools', 'b': 'functools', 'c': 'collections', 'd': 'struct',
                'ans': 'C', 'exp': 'The "collections" module provides specialized container datatypes including deque, Counter, OrderedDict, and defaultdict.'
            },
            {
                'cat': 'python-programming', 'diff': 'medium',
                'q': 'What does the functools.wraps decorator do when writing custom decorators?',
                'a': 'Caches function results', 'b': 'Preserves the original function name and docstring metadata', 'c': 'Runs the function asynchronously', 'd': 'Validates arguments',
                'ans': 'B', 'exp': '@functools.wraps copies the __name__, __doc__, and other attributes from the wrapped function to the wrapper.'
            },
            {
                'cat': 'python-programming', 'diff': 'hard',
                'q': 'What happens if you use a mutable object like a list as a default parameter in a Python function?',
                'a': 'A new list is created each call', 'b': 'A SyntaxError is raised', 'c': 'The same list object is shared across all function calls', 'd': 'Python converts it to a tuple',
                'ans': 'C', 'exp': 'Default parameter values are evaluated once when the function definition is executed, so mutable defaults are shared across subsequent invocations.'
            },
            {
                'cat': 'python-programming', 'diff': 'easy',
                'q': 'Which statement safely handles exceptions in Python?',
                'a': 'try / catch', 'b': 'try / except', 'c': 'check / rescue', 'd': 'attempt / recover',
                'ans': 'B', 'exp': 'Python uses "try" blocks followed by "except" blocks to catch and handle exceptions.'
            },

            # --- Computer Science ---
            {
                'cat': 'computer-science', 'diff': 'easy',
                'q': 'What is the time complexity of looking up a key in a balanced hash table on average?',
                'a': 'O(n)', 'b': 'O(log n)', 'c': 'O(1)', 'd': 'O(n log n)',
                'ans': 'C', 'exp': 'Hash tables provide O(1) average time complexity for insertions and lookups.'
            },
            {
                'cat': 'computer-science', 'diff': 'easy',
                'q': 'Which data structure follows the Last-In, First-Out (LIFO) principle?',
                'a': 'Queue', 'b': 'Stack', 'c': 'Linked List', 'd': 'Binary Tree',
                'ans': 'B', 'exp': 'A Stack operates on LIFO (the last element pushed is the first to be popped).'
            },
            {
                'cat': 'computer-science', 'diff': 'medium',
                'q': 'What type of graph has directed edges and no cycles?',
                'a': 'Bipartite Graph', 'b': 'Complete Graph', 'c': 'Directed Acyclic Graph (DAG)', 'd': 'Eulerian Graph',
                'ans': 'C', 'exp': 'A DAG is a directed graph with no directed cycles, widely used in scheduling and compilers.'
            },
            {
                'cat': 'computer-science', 'diff': 'medium',
                'q': 'Which sorting algorithm has a guaranteed worst-case time complexity of O(n log n)?',
                'a': 'Quick Sort', 'b': 'Merge Sort', 'c': 'Bubble Sort', 'd': 'Selection Sort',
                'ans': 'B', 'exp': 'Merge Sort always splits and merges arrays in O(n log n) time in all cases (best, average, worst).'
            },
            {
                'cat': 'computer-science', 'diff': 'hard',
                'q': 'Which problem is proven to be NP-complete?',
                'a': 'Shortest Path (Dijkstra)', 'b': 'Minimum Spanning Tree (Kruskal)', 'c': 'Boolean Satisfiability (SAT)', 'd': 'Sorting integers',
                'ans': 'C', 'exp': 'The Cook-Levin theorem proved that the Boolean Satisfiability Problem (SAT) is NP-complete.'
            },
            {
                'cat': 'computer-science', 'diff': 'medium',
                'q': 'In operating systems, which condition is NOT one of Coffman\'s four deadlock conditions?',
                'a': 'Mutual Exclusion', 'b': 'Hold and Wait', 'c': 'Preemption allowed', 'd': 'Circular Wait',
                'ans': 'C', 'exp': 'The condition is "No preemption"; allowing preemption actually breaks deadlock.'
            },
            {
                'cat': 'computer-science', 'diff': 'hard',
                'q': 'What is the purpose of the Translation Lookaside Buffer (TLB) in a CPU?',
                'a': 'Translates assembly to machine code', 'b': 'Caches virtual-to-physical address translations', 'c': 'Buffers I/O bus signals', 'd': 'Performs branch prediction',
                'ans': 'B', 'exp': 'The TLB is a high-speed hardware memory cache that stores recent virtual-to-physical address translations.'
            },
            {
                'cat': 'computer-science', 'diff': 'easy',
                'q': 'What base numbering system does hexadecimal use?',
                'a': 'Base 2', 'b': 'Base 8', 'c': 'Base 10', 'd': 'Base 16',
                'ans': 'D', 'exp': 'Hexadecimal represents numbers in base 16, using digits 0-9 and letters A-F.'
            },
            {
                'cat': 'computer-science', 'diff': 'medium',
                'q': 'Which layer of the OSI model does the TCP protocol belong to?',
                'a': 'Network Layer (Layer 3)', 'b': 'Transport Layer (Layer 4)', 'c': 'Session Layer (Layer 5)', 'd': 'Data Link Layer (Layer 2)',
                'ans': 'B', 'exp': 'TCP (Transmission Control Protocol) operates at Layer 4: the Transport layer.'
            },
            {
                'cat': 'computer-science', 'diff': 'hard',
                'q': 'What does ACID stand for in database transaction management?',
                'a': 'Atomicity, Consistency, Isolation, Durability', 'b': 'Access, Control, Integrity, Data', 'c': 'Asynchronous, Concurrent, Indexed, Distributed', 'd': 'Allocation, Cache, Interface, Driver',
                'ans': 'A', 'exp': 'ACID guarantees database reliability: Atomicity, Consistency, Isolation, and Durability.'
            },
            {
                'cat': 'computer-science', 'diff': 'easy',
                'q': 'How many bits are in one standard byte?',
                'a': '4', 'b': '8', 'c': '16', 'd': '32',
                'ans': 'B', 'exp': 'There are 8 bits in one byte.'
            },
            {
                'cat': 'computer-science', 'diff': 'medium',
                'q': 'Which tree traversal visits nodes in the order: Left Subtree, Root, Right Subtree?',
                'a': 'Pre-order', 'b': 'In-order', 'c': 'Post-order', 'd': 'Level-order',
                'ans': 'B', 'exp': 'In-order traversal visits left child, root, and then right child.'
            },
            {
                'cat': 'computer-science', 'diff': 'medium',
                'q': 'What algorithm is used to find the shortest path between nodes in a weighted graph with non-negative edge weights?',
                'a': 'Dijkstra\'s algorithm', 'b': 'Depth-First Search', 'c': 'Binary Search', 'd': 'Prim\'s algorithm',
                'ans': 'A', 'exp': 'Dijkstra\'s algorithm calculates the shortest path from a starting node to all other nodes.'
            },
            {
                'cat': 'computer-science', 'diff': 'hard',
                'q': 'What is the time complexity of building a Binary Heap from an unordered array of n elements?',
                'a': 'O(n log n)', 'b': 'O(n)', 'c': 'O(log n)', 'd': 'O(n^2)',
                'ans': 'B', 'exp': 'Using the bottom-up Floyd\'s heapify approach, building a heap takes linear O(n) time.'
            },
            {
                'cat': 'computer-science', 'diff': 'easy',
                'q': 'Which data structure is best suited for implementing Breadth-First Search (BFS)?',
                'a': 'Queue', 'b': 'Stack', 'c': 'Max-Heap', 'd': 'Trie',
                'ans': 'A', 'exp': 'BFS uses a FIFO Queue to visit neighbor vertices level by level.'
            },

            # --- Web Development ---
            {
                'cat': 'web-development', 'diff': 'easy',
                'q': 'Which HTTP status code indicates a successful request?',
                'a': '200 OK', 'b': '301 Moved Permanently', 'c': '404 Not Found', 'd': '500 Server Error',
                'ans': 'A', 'exp': 'HTTP 200 OK signifies that the server successfully processed the request.'
            },
            {
                'cat': 'web-development', 'diff': 'easy',
                'q': 'What does CSS stand for?',
                'a': 'Computer Style Sheets', 'b': 'Cascading Style Sheets', 'c': 'Creative Script Styles', 'd': 'Content Styler System',
                'ans': 'B', 'exp': 'CSS stands for Cascading Style Sheets.'
            },
            {
                'cat': 'web-development', 'diff': 'medium',
                'q': 'In JavaScript, what will typeof NaN return?',
                'a': '"undefined"', 'b': '"nan"', 'c': '"number"', 'd': '"object"',
                'ans': 'C', 'exp': 'Despite representing "Not-a-Number", NaN is of type "number" in the IEEE-754 standard and JavaScript.'
            },
            {
                'cat': 'web-development', 'diff': 'medium',
                'q': 'Which HTTP header prevents cross-origin sites from embedding your page in an iframe?',
                'a': 'X-Content-Type-Options', 'b': 'X-Frame-Options', 'c': 'Access-Control-Allow-Origin', 'd': 'Strict-Transport-Security',
                'ans': 'B', 'exp': 'X-Frame-Options (DENY / SAMEORIGIN) instructs the browser whether iframe embedding is permitted to prevent Clickjacking.'
            },
            {
                'cat': 'web-development', 'diff': 'hard',
                'q': 'What protocol does HTTP/3 use as its underlying transport layer instead of TCP?',
                'a': 'UDP with QUIC', 'b': 'SCTP', 'c': 'Raw WebSockets', 'd': 'IPsec',
                'ans': 'A', 'exp': 'HTTP/3 is built on QUIC, an encrypted multiplexed transport protocol over UDP.'
            },
            {
                'cat': 'web-development', 'diff': 'medium',
                'q': 'Which JavaScript event loop phase executes resolved Promises before setTimeout callbacks?',
                'a': 'Macro-task queue', 'b': 'Micro-task queue', 'c': 'Render phase', 'd': 'I/O poll phase',
                'ans': 'B', 'exp': 'Promises run in the microtask queue, which is emptied immediately after the current execution context and before macro-tasks.'
            },
            {
                'cat': 'web-development', 'diff': 'easy',
                'q': 'Which HTML5 element is used to play audio clips without third-party plugins?',
                'a': '<sound>', 'b': '<audio>', 'c': '<music>', 'd': '<media>',
                'ans': 'B', 'exp': 'HTML5 introduced the standard <audio> tag for embedded audio streams.'
            },
            {
                'cat': 'web-development', 'diff': 'hard',
                'q': 'What is the purpose of the "SameSite" attribute in HTTP Cookies?',
                'a': 'Encrypts cookie payload', 'b': 'Prevents Cross-Site Request Forgery (CSRF) attacks', 'c': 'Sets expiration date', 'd': 'Enforces HTTPS only',
                'ans': 'B', 'exp': 'SameSite (Strict / Lax) prevents cookies from being sent with cross-site requests, mitigating CSRF.'
            },
            {
                'cat': 'web-development', 'diff': 'medium',
                'q': 'What does CORS stand for in web security?',
                'a': 'Cross-Origin Resource Sharing', 'b': 'Centralized Origin Routing System', 'c': 'Cookie Origin Remote Storage', 'd': 'Client Oriented Resource Standard',
                'ans': 'A', 'exp': 'CORS stands for Cross-Origin Resource Sharing.'
            },
            {
                'cat': 'web-development', 'diff': 'easy',
                'q': 'Which keyword declares a block-scoped reassignable variable in modern JavaScript?',
                'a': 'var', 'b': 'let', 'c': 'const', 'd': 'def',
                'ans': 'B', 'exp': '"let" declares block-scoped variables that can be reassigned.'
            },
            {
                'cat': 'web-development', 'diff': 'medium',
                'q': 'What does the CSS property "box-sizing: border-box" do?',
                'a': 'Removes borders', 'b': 'Includes padding and border within the element\'s total width and height', 'c': 'Adds shadow to borders', 'd': 'Centers the box',
                'ans': 'B', 'exp': 'border-box makes width and height calculations include content, padding, and borders.'
            },
            {
                'cat': 'web-development', 'diff': 'hard',
                'q': 'What WebSocket frame opcode indicates a connection close handshake?',
                'a': '0x1', 'b': '0x8', 'c': '0x9', 'd': '0xA',
                'ans': 'B', 'exp': 'RFC 6455 specifies opcode 0x8 denotes a connection close control frame (0x9 is ping, 0xA is pong).'
            },
            {
                'cat': 'web-development', 'diff': 'easy',
                'q': 'What protocol provides secure, encrypted web browsing?',
                'a': 'HTTP', 'b': 'FTP', 'c': 'HTTPS', 'd': 'SMTP',
                'ans': 'C', 'exp': 'HTTPS (HTTP over TLS) encrypts all communication between browser and server.'
            },
            {
                'cat': 'web-development', 'diff': 'medium',
                'q': 'In modern CSS, which layout system is primarily two-dimensional (rows and columns simultaneously)?',
                'a': 'Flexbox', 'b': 'CSS Grid', 'c': 'Float', 'd': 'Inline-block',
                'ans': 'B', 'exp': 'CSS Grid is a 2D layout model handling both rows and columns at once, while Flexbox is primarily 1D.'
            },
            {
                'cat': 'web-development', 'diff': 'hard',
                'q': 'Which HTTP status code signifies "429"?',
                'a': 'Payment Required', 'b': 'Too Many Requests', 'c': 'Unavailable For Legal Reasons', 'd': 'Bad Gateway',
                'ans': 'B', 'exp': 'HTTP 429 Too Many Requests indicates rate limiting.'
            },

            # --- Cybersecurity ---
            {
                'cat': 'cybersecurity', 'diff': 'easy',
                'q': 'What type of malicious attack overwhelms a server with fake traffic to take it offline?',
                'a': 'SQL Injection', 'b': 'Distributed Denial of Service (DDoS)', 'c': 'Cross-Site Scripting (XSS)', 'd': 'Phishing',
                'ans': 'B', 'exp': 'DDoS floods target servers with massive traffic to render them unavailable.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'easy',
                'q': 'What does 2FA stand for in account protection?',
                'a': 'Two-Factor Authentication', 'b': 'Two-File Archiving', 'c': 'Twin Firewall Architecture', 'd': 'Triple Fast Authorization',
                'ans': 'A', 'exp': 'Two-Factor Authentication adds a secondary verification layer beyond passwords.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'medium',
                'q': 'Which vulnerability occurs when user input is executed directly as database queries?',
                'a': 'CSRF', 'b': 'SQL Injection (SQLi)', 'c': 'Buffer Overflow', 'd': 'Man-in-the-Middle',
                'ans': 'B', 'exp': 'SQL Injection occurs when untrusted input is concatenated into dynamic SQL statements.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'medium',
                'q': 'Which hashing algorithm is considered cryptographically broken and unsafe for passwords?',
                'a': 'bcrypt', 'b': 'Argon2id', 'c': 'MD5', 'd': 'PBKDF2',
                'ans': 'C', 'exp': 'MD5 is vulnerable to collision attacks and is far too fast for secure password hashing.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'hard',
                'q': 'In asymmetric cryptography, which key is used to decrypt a message encrypted with a user\'s public key?',
                'a': 'Public key', 'b': 'Private key', 'c': 'Symmetric key', 'd': 'HMAC key',
                'ans': 'B', 'exp': 'Data encrypted with a recipient\'s public key can only be decrypted by the matching private key.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'medium',
                'q': 'What is a "Salt" in the context of password security?',
                'a': 'A secret key kept on another server', 'b': 'Random data appended to a password before hashing to prevent rainbow table attacks', 'c': 'An encryption algorithm', 'd': 'A firewall rule',
                'ans': 'B', 'exp': 'A salt is a unique random string added to passwords before hashing to defeat precomputed rainbow tables.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'hard',
                'q': 'What type of attack involves an attacker tricking a victim\'s browser into executing authenticated requests on a vulnerable site?',
                'a': 'Cross-Site Request Forgery (CSRF)', 'b': 'Reflected XSS', 'c': 'DNS Poisoning', 'd': 'Clickjacking',
                'ans': 'A', 'exp': 'CSRF abuses the browser\'s automatic cookie submission to forge unwanted authenticated actions.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'easy',
                'q': 'What is social engineering in the context of security?',
                'a': 'Hacking into social media', 'b': 'Manipulating people into revealing confidential information', 'c': 'Building social apps', 'd': 'Encrypting chat messages',
                'ans': 'B', 'exp': 'Social engineering targets human psychology to trick individuals into disclosing sensitive data.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'medium',
                'q': 'Which Wi-Fi security standard is the most modern and secure for personal networks?',
                'a': 'WEP', 'b': 'WPA', 'c': 'WPA2', 'd': 'WPA3',
                'ans': 'D', 'exp': 'WPA3 is the latest Wi-Fi security standard, featuring robust protection against offline dictionary attacks.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'hard',
                'q': 'What is the Diffie-Hellman algorithm used for?',
                'a': 'Symmetric file encryption', 'b': 'Secure key exchange over an insecure channel', 'c': 'Password hashing', 'd': 'Malware scanning',
                'ans': 'B', 'exp': 'Diffie-Hellman allows two parties to establish a shared secret key over an unencrypted network.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'easy',
                'q': 'What port does secure SSH traffic typically use by default?',
                'a': '21', 'b': '22', 'c': '80', 'd': '443',
                'ans': 'B', 'exp': 'Port 22 is the standard port for SSH (Secure Shell).'
            },
            {
                'cat': 'cybersecurity', 'diff': 'medium',
                'q': 'What does a penetration tester simulate?',
                'a': 'User traffic tests', 'b': 'Cyber attacks to identify security weaknesses before criminals do', 'c': 'Hardware manufacturing', 'd': 'Data backups',
                'ans': 'B', 'exp': 'Penetration testing is ethical hacking to find and patch vulnerabilities.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'hard',
                'q': 'What does the acronym CIA triad represent in information security?',
                'a': 'Central Intelligence Agency', 'b': 'Confidentiality, Integrity, Availability', 'c': 'Control, Identification, Authentication', 'd': 'Cryptography, Inspection, Auditing',
                'ans': 'B', 'exp': 'The CIA triad (Confidentiality, Integrity, Availability) forms the cornerstone of cybersecurity principles.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'easy',
                'q': 'What malicious software encrypts user files and demands ransom money to decrypt them?',
                'a': 'Spyware', 'b': 'Ransomware', 'c': 'Adware', 'd': 'Rootkit',
                'ans': 'B', 'exp': 'Ransomware encrypts target data and demands payment for the decryption key.'
            },
            {
                'cat': 'cybersecurity', 'diff': 'medium',
                'q': 'What security control prevents malicious JavaScript from accessing document.cookie?',
                'a': 'HttpOnly flag', 'b': 'Secure flag', 'c': 'Path attribute', 'd': 'Domain attribute',
                'ans': 'A', 'exp': 'Setting the HttpOnly flag blocks client-side scripts from reading session cookies via document.cookie.'
            },

            # --- General Knowledge ---
            {
                'cat': 'general-knowledge', 'diff': 'easy',
                'q': 'What is the capital city of Australia?',
                'a': 'Sydney', 'b': 'Melbourne', 'c': 'Canberra', 'd': 'Brisbane',
                'ans': 'C', 'exp': 'Canberra is the federal capital of Australia, chosen as a compromise between Sydney and Melbourne.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'easy',
                'q': 'How many continents are there on Earth?',
                'a': '5', 'b': '6', 'c': '7', 'd': '8',
                'ans': 'C', 'exp': 'Earth has 7 continents: Asia, Africa, North America, South America, Antarctica, Europe, and Australia.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'medium',
                'q': 'Who painted the famous masterpiece "The Starry Night"?',
                'a': 'Pablo Picasso', 'b': 'Vincent van Gogh', 'c': 'Claude Monet', 'd': 'Leonardo da Vinci',
                'ans': 'B', 'exp': 'Vincent van Gogh painted The Starry Night in June 1889 while at the Saint-Paul-de-Mausole asylum.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'medium',
                'q': 'Which country has the longest coastline in the world?',
                'a': 'Russia', 'b': 'Canada', 'c': 'Indonesia', 'd': 'Australia',
                'ans': 'B', 'exp': 'Canada has the world\'s longest coastline, stretching over 202,080 kilometers.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'hard',
                'q': 'In what year did the Apollo 11 mission successfully land astronauts on the Moon?',
                'a': '1965', 'b': '1969', 'c': '1971', 'd': '1973',
                'ans': 'B', 'exp': 'Apollo 11 landed on the Moon on July 20, 1969, with Neil Armstrong and Buzz Aldrin.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'easy',
                'q': 'What is the largest ocean on Earth?',
                'a': 'Atlantic Ocean', 'b': 'Indian Ocean', 'c': 'Pacific Ocean', 'd': 'Arctic Ocean',
                'ans': 'C', 'exp': 'The Pacific Ocean is the largest and deepest ocean on Earth.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'medium',
                'q': 'What ancient wonder was located in Alexandria, Egypt?',
                'a': 'Colossus of Rhodes', 'b': 'Hanging Gardens', 'c': 'Lighthouse of Alexandria', 'd': 'Temple of Artemis',
                'ans': 'C', 'exp': 'The Lighthouse of Alexandria (Pharos) was built by the Ptolemaic Kingdom around 280 BC.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'hard',
                'q': 'Which chemical element is named after the creator of the periodic table?',
                'a': 'Curium', 'b': 'Mendelevium', 'c': 'Einsteinium', 'd': 'Nobelium',
                'ans': 'B', 'exp': 'Mendelevium (element 101, Md) was named in honor of Dmitri Mendeleev.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'easy',
                'q': 'Which currency is used in Japan?',
                'a': 'Yuan', 'b': 'Won', 'c': 'Yen', 'd': 'Ringgit',
                'ans': 'C', 'exp': 'The Japanese Yen (¥) is the official currency of Japan.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'medium',
                'q': 'What is the tallest mountain peak in the world above sea level?',
                'a': 'K2', 'b': 'Mount Everest', 'c': 'Kangchenjunga', 'd': 'Lhotse',
                'ans': 'B', 'exp': 'Mount Everest rises 8,848.86 meters above sea level in the Himalayas.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'hard',
                'q': 'Who was the first woman to win a Nobel Prize (and the only person to win in two different sciences)?',
                'a': 'Rosalind Franklin', 'b': 'Marie Curie', 'c': 'Ada Lovelace', 'd': 'Dorothy Hodgkin',
                'ans': 'B', 'exp': 'Marie Curie won the Nobel Prize in Physics (1903) and Chemistry (1911).'
            },
            {
                'cat': 'general-knowledge', 'diff': 'easy',
                'q': 'What animal is known as the "King of the Jungle"?',
                'a': 'Tiger', 'b': 'Lion', 'c': 'Elephant', 'd': 'Gorilla',
                'ans': 'B', 'exp': 'The Lion is colloquially known as the King of the Jungle.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'medium',
                'q': 'What is the smallest country in the world by land area?',
                'a': 'Monaco', 'b': 'Nauru', 'c': 'Vatican City', 'd': 'San Marino',
                'ans': 'C', 'exp': 'Vatican City is the smallest independent state, measuring just 0.49 square kilometers.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'hard',
                'q': 'What year did the Berlin Wall fall, leading to German reunification?',
                'a': '1987', 'b': '1989', 'c': '1991', 'd': '1993',
                'ans': 'B', 'exp': 'The Berlin Wall fell on November 9, 1989.'
            },
            {
                'cat': 'general-knowledge', 'diff': 'easy',
                'q': 'Which primary color mixed with red makes purple?',
                'a': 'Yellow', 'b': 'Blue', 'c': 'Green', 'd': 'White',
                'ans': 'B', 'exp': 'Red combined with Blue produces purple.'
            },

            # --- Science & Technology ---
            {
                'cat': 'science-technology', 'diff': 'easy',
                'q': 'What gas do humans inhale to support cellular respiration?',
                'a': 'Nitrogen', 'b': 'Oxygen', 'c': 'Carbon Dioxide', 'd': 'Hydrogen',
                'ans': 'B', 'exp': 'Oxygen is required for aerobic cellular respiration in human cells.'
            },
            {
                'cat': 'science-technology', 'diff': 'easy',
                'q': 'What planet in our solar system is known as the "Red Planet"?',
                'a': 'Venus', 'b': 'Mars', 'c': 'Jupiter', 'd': 'Mercury',
                'ans': 'B', 'exp': 'Mars appears red due to abundant iron oxide (rust) on its surface.'
            },
            {
                'cat': 'science-technology', 'diff': 'medium',
                'q': 'What fundamental subatomic particle has a negative electrical charge?',
                'a': 'Proton', 'b': 'Neutron', 'c': 'Electron', 'd': 'Positron',
                'ans': 'C', 'exp': 'Electrons carry a negative elementary charge.'
            },
            {
                'cat': 'science-technology', 'diff': 'medium',
                'q': 'What is the speed of light in a vacuum approximately?',
                'a': '300,000 km/s', 'b': '150,000 km/s', 'c': '1,000,000 km/s', 'd': '3,000 km/s',
                'ans': 'A', 'exp': 'The speed of light in vacuum is approximately 299,792 km/s (roughly 300,000 km/s).'
            },
            {
                'cat': 'science-technology', 'diff': 'hard',
                'q': 'In quantum physics, what principle states that you cannot simultaneously measure position and momentum with arbitrary precision?',
                'a': 'Pauli Exclusion Principle', 'b': 'Heisenberg Uncertainty Principle', 'c': 'Schrödinger Wave Equation', 'd': 'Planck\'s Law',
                'ans': 'B', 'exp': 'Werner Heisenberg formulated the uncertainty principle stating Δx · Δp ≥ ℏ/2.'
            },
            {
                'cat': 'science-technology', 'diff': 'medium',
                'q': 'What is the powerhouse organelle of eukaryotic cells?',
                'a': 'Ribosome', 'b': 'Mitochondria', 'c': 'Golgi apparatus', 'd': 'Endoplasmic reticulum',
                'ans': 'B', 'exp': 'Mitochondria generate most of the cell\'s chemical energy in the form of ATP.'
            },
            {
                'cat': 'science-technology', 'diff': 'hard',
                'q': 'What astronomical boundary around a black hole marks the point of no return for light?',
                'a': 'Accretion Disk', 'b': 'Singularity', 'c': 'Event Horizon', 'd': 'Photon Sphere',
                'ans': 'C', 'exp': 'The event horizon is the threshold where gravitational pull prevents even light from escaping.'
            },
            {
                'cat': 'science-technology', 'diff': 'easy',
                'q': 'What is the chemical formula for ordinary pure water?',
                'a': 'CO2', 'b': 'NaCl', 'c': 'H2O', 'd': 'O2',
                'ans': 'C', 'exp': 'Water consists of two hydrogen atoms bonded to one oxygen atom (H2O).'
            },
            {
                'cat': 'science-technology', 'diff': 'medium',
                'q': 'Who proposed the Theory of General Relativity in 1915?',
                'a': 'Isaac Newton', 'b': 'Albert Einstein', 'c': 'Niels Bohr', 'd': 'Max Planck',
                'ans': 'B', 'exp': 'Albert Einstein published the general theory of relativity in 1915.'
            },
            {
                'cat': 'science-technology', 'diff': 'hard',
                'q': 'What type of neural network architecture with self-attention mechanisms forms the foundation for modern Large Language Models (LLMs)?',
                'a': 'Convolutional Neural Network (CNN)', 'b': 'Transformer', 'c': 'Recurrent Neural Network (RNN)', 'd': 'Self-Organizing Map (SOM)',
                'ans': 'B', 'exp': 'The Transformer architecture introduced in the 2017 paper "Attention Is All You Need" powers modern LLMs.'
            },
            {
                'cat': 'science-technology', 'diff': 'easy',
                'q': 'Which element has the atomic number 1?',
                'a': 'Helium', 'b': 'Hydrogen', 'c': 'Carbon', 'd': 'Oxygen',
                'ans': 'B', 'exp': 'Hydrogen is the lightest element with atomic number 1.'
            },
            {
                'cat': 'science-technology', 'diff': 'medium',
                'q': 'What is the term for computer software that mimics human cognitive functions like learning and problem-solving?',
                'a': 'Cloud Computing', 'b': 'Artificial Intelligence', 'c': 'Quantum Simulation', 'd': 'Blockchain',
                'ans': 'B', 'exp': 'Artificial Intelligence (AI) simulates human intelligence processes in computing systems.'
            },
            {
                'cat': 'science-technology', 'diff': 'hard',
                'q': 'What semiconductor device revolutionized electronics by replacing bulky vacuum tubes in 1947?',
                'a': 'Capacitor', 'b': 'Inductor', 'c': 'Transistor', 'd': 'Resistor',
                'ans': 'C', 'exp': 'The transistor was invented at Bell Labs in 1947, enabling modern miniaturized microchips.'
            },
            {
                'cat': 'science-technology', 'diff': 'easy',
                'q': 'What force pulls objects toward the center of the Earth?',
                'a': 'Magnetism', 'b': 'Centrifugal force', 'c': 'Gravity', 'd': 'Atmospheric pressure',
                'ans': 'C', 'exp': 'Gravity is the universal attractive force between massive bodies.'
            },
            {
                'cat': 'science-technology', 'diff': 'medium',
                'q': 'What space telescope was launched in December 2021 to succeed Hubble with infrared observation?',
                'a': 'Kepler', 'b': 'James Webb Space Telescope (JWST)', 'c': 'Spitzer', 'd': 'Chandra',
                'ans': 'B', 'exp': 'JWST conducts infrared astronomy to observe the earliest galaxies formed after the Big Bang.'
            },

            # --- Mathematics & Logic ---
            {
                'cat': 'mathematics-logic', 'diff': 'easy',
                'q': 'What is the sum of angles in a flat Euclidean triangle?',
                'a': '90 degrees', 'b': '180 degrees', 'c': '270 degrees', 'd': '360 degrees',
                'ans': 'B', 'exp': 'The interior angles of any triangle in Euclidean plane geometry sum to 180 degrees.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'easy',
                'q': 'What is 7 multiplied by 8?',
                'a': '54', 'b': '56', 'c': '58', 'd': '64',
                'ans': 'B', 'exp': '7 × 8 = 56.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'medium',
                'q': 'If a fair coin is tossed 3 times, what is the probability of getting exactly 3 heads?',
                'a': '1/2', 'b': '1/4', 'c': '1/8', 'd': '1/16',
                'ans': 'C', 'exp': '(1/2) × (1/2) × (1/2) = 1/8.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'medium',
                'q': 'What is the next number in the Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, ...?',
                'a': '18', 'b': '21', 'c': '24', 'd': '26',
                'ans': 'B', 'exp': 'Each Fibonacci number is the sum of the previous two: 8 + 13 = 21.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'hard',
                'q': 'What is the derivative of f(x) = ln(x) with respect to x (for x > 0)?',
                'a': '1/x', 'b': 'e^x', 'c': 'x', 'd': '1/(x^2)',
                'ans': 'A', 'exp': 'The derivative of the natural logarithm ln(x) is 1/x.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'medium',
                'q': 'What is the value of 5! (5 factorial)?',
                'a': '60', 'b': '100', 'c': '120', 'd': '150',
                'ans': 'C', 'exp': '5! = 5 × 4 × 3 × 2 × 1 = 120.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'hard',
                'q': 'In the Monty Hall problem with 3 doors, what is your probability of winning if you switch doors after the host reveals a goat?',
                'a': '1/3', 'b': '1/2', 'c': '2/3', 'd': '3/4',
                'ans': 'C', 'exp': 'Switching doors gives you a 2/3 chance of winning the car.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'easy',
                'q': 'What is the square root of 144?',
                'a': '11', 'b': '12', 'c': '13', 'd': '14',
                'ans': 'B', 'exp': '12 × 12 = 144.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'medium',
                'q': 'If a clock shows 3:15, what is the exact angle between the hour hand and the minute hand?',
                'a': '0 degrees', 'b': '7.5 degrees', 'c': '15 degrees', 'd': '22.5 degrees',
                'ans': 'B', 'exp': 'At 3:15, the hour hand has moved 15/60 of 30° = 7.5° past the 3.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'hard',
                'q': 'What is Euler\'s identity relating five fundamental mathematical constants?',
                'a': 'e^(iπ) + 1 = 0', 'b': 'E = mc²', 'c': 'a² + b² = c²', 'd': 'sin²(x) + cos²(x) = 1',
                'ans': 'A', 'exp': 'Euler\'s identity e^(iπ) + 1 = 0 combines e, i, π, 1, and 0.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'easy',
                'q': 'Which number is neither prime nor composite?',
                'a': '0', 'b': '1', 'c': '2', 'd': '3',
                'ans': 'B', 'exp': 'By definition, 1 is a unit, neither prime nor composite.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'medium',
                'q': 'What is the median of this dataset: [3, 7, 9, 15, 21]?',
                'a': '7', 'b': '9', 'c': '11', 'd': '15',
                'ans': 'B', 'exp': 'The middle element in the sorted five-element list is 9.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'hard',
                'q': 'What is the solution to log_2(64)?',
                'a': '4', 'b': '5', 'c': '6', 'd': '8',
                'ans': 'C', 'exp': '2^6 = 64, so log_2(64) = 6.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'easy',
                'q': 'What geometric shape has 8 straight sides?',
                'a': 'Hexagon', 'b': 'Heptagon', 'c': 'Octagon', 'd': 'Decagon',
                'ans': 'C', 'exp': 'An octagon is an eight-sided polygon.'
            },
            {
                'cat': 'mathematics-logic', 'diff': 'medium',
                'q': 'A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?',
                'a': '$0.10', 'b': '$0.05', 'c': '$0.01', 'd': '$0.15',
                'ans': 'B', 'exp': 'Ball + (Ball + $1.00) = $1.10 -> 2 × Ball = $0.10 -> Ball = $0.05.'
            },

            # --- Gaming & Pop Culture ---
            {
                'cat': 'gaming-pop-culture', 'diff': 'easy',
                'q': 'Which iconic Nintendo character is a plumber who saves Princess Peach in the Mushroom Kingdom?',
                'a': 'Link', 'b': 'Mario', 'c': 'Donkey Kong', 'd': 'Zelda',
                'ans': 'B', 'exp': 'Mario is Nintendo\'s flagship mascot, created by Shigeru Miyamoto.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'easy',
                'q': 'Which block-building sandbox game created by Mojang is the best-selling video game of all time?',
                'a': 'Roblox', 'b': 'Terraria', 'c': 'Minecraft', 'd': 'Fortnite',
                'ans': 'C', 'exp': 'Minecraft has sold over 300 million copies worldwide.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'medium',
                'q': 'What is the name of the protagonist\'s artificial intelligence companion in the "Halo" franchise?',
                'a': 'GLADoS', 'b': 'Cortana', 'c': 'SIRI', 'd': 'EDI',
                'ans': 'B', 'exp': 'Cortana is Master Chief\'s AI partner throughout the Halo series.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'medium',
                'q': 'In "The Witcher 3: Wild Hunt", what is the name of Geralt of Rivia\'s horse?',
                'a': 'Shadowmere', 'b': 'Roach', 'c': 'Epona', 'd': 'Agro',
                'ans': 'B', 'exp': 'Geralt names all of his horses Roach (Płotka in Polish).'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'hard',
                'q': 'In what year was the original PlayStation console released by Sony in Japan?',
                'a': '1992', 'b': '1994', 'c': '1996', 'd': '1998',
                'ans': 'B', 'exp': 'The Sony PlayStation launched in Japan on December 3, 1994.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'medium',
                'q': 'What esports title features Champions, Summoner\'s Rift, and the annual Worlds tournament?',
                'a': 'Dota 2', 'b': 'League of Legends', 'c': 'Overwatch', 'd': 'Valorant',
                'ans': 'B', 'exp': 'League of Legends by Riot Games features Summoner\'s Rift and Worlds.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'easy',
                'q': 'Which gaming company created "Pokémon", "The Legend of Zelda", and "Super Smash Bros."?',
                'a': 'Sega', 'b': 'Nintendo', 'c': 'Capcom', 'd': 'Bandai Namco',
                'ans': 'B', 'exp': 'Nintendo is the creator and publisher of these legendary franchises.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'hard',
                'q': 'What was the first commercially successful coin-operated arcade video game, released in 1972 by Atari?',
                'a': 'Space Invaders', 'b': 'Pong', 'c': 'Asteroids', 'd': 'Pac-Man',
                'ans': 'B', 'exp': 'Pong, developed by Allan Alcorn and released by Atari in 1972, popularized the video game industry.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'easy',
                'q': 'What yellow dot-eating arcade character was chased by Blinky, Pinky, Inky, and Clyde?',
                'a': 'Q*bert', 'b': 'Dig Dug', 'c': 'Pac-Man', 'd': 'Frogger',
                'ans': 'C', 'exp': 'Pac-Man, created by Toru Iwatani in 1980, is pursued by four colorful ghosts.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'medium',
                'q': 'In "Dark Souls", what phrase appears on screen when your character perishes?',
                'a': 'GAME OVER', 'b': 'YOU DIED', 'c': 'WASTED', 'd': 'DEFEAT',
                'ans': 'B', 'exp': '"YOU DIED" in crimson letters is the iconic death notification in the Souls series.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'hard',
                'q': 'What is the title of the fictional language created for the dragons in "The Elder Scrolls V: Skyrim"?',
                'a': 'Dovahzul', 'b': 'Simlish', 'c': 'Sindarin', 'd': 'Klingon',
                'ans': 'A', 'exp': 'Dovahzul is the dragon tongue spoken in Skyrim.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'easy',
                'q': 'Which battle royale game features 100 players jumping from a "Battle Bus" and building structures?',
                'a': 'Apex Legends', 'b': 'PUBG', 'c': 'Fortnite', 'd': 'Warzone',
                'ans': 'C', 'exp': 'Fortnite by Epic Games features the Battle Bus and real-time building mechanics.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'medium',
                'q': 'What company developed the Steam distribution platform and the "Half-Life" series?',
                'a': 'Blizzard', 'b': 'Valve', 'c': 'Electronic Arts', 'd': 'Ubisoft',
                'ans': 'B', 'exp': 'Valve Corporation developed Half-Life, Portal, Counter-Strike, and Steam.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'hard',
                'q': 'What famous secret cheat code is "Up, Up, Down, Down, Left, Right, Left, Right, B, A"?',
                'a': 'The Capcom Code', 'b': 'The Konami Code', 'c': 'The Sega Secret', 'd': 'The id Software Code',
                'ans': 'B', 'exp': 'The Konami Code was created by Kazuhisa Hashimoto for Gradius on the NES in 1986.'
            },
            {
                'cat': 'gaming-pop-culture', 'diff': 'medium',
                'q': 'Who is the main protagonist of the "God of War" franchise, known as the Ghost of Sparta?',
                'a': 'Ares', 'b': 'Kratos', 'c': 'Atreus', 'd': 'Zeus',
                'ans': 'B', 'exp': 'Kratos is the Spartan warrior protagonist of God of War.'
            }
        ]

        for q_data in raw_questions:
            cat = cat_objs.get(q_data['cat'])
            if not cat:
                continue
            question = Question(
                category_id=cat.id,
                difficulty=q_data['diff'],
                question_text=q_data['q'],
                option_a=q_data['a'],
                option_b=q_data['b'],
                option_c=q_data['c'],
                option_d=q_data['d'],
                correct_option=q_data['ans'],
                explanation=q_data['exp']
            )
            db.session.add(question)

        db.session.flush()

        # 4. Create Demo Users & Stats
        demo_users = [
            {'username': 'admin', 'email': 'admin@quizclash.gg', 'pass': 'admin123', 'avatar': 'code_wizard', 'admin': True},
            {'username': 'cyber_ninja', 'email': 'ninja@quizclash.gg', 'pass': 'demo123', 'avatar': 'cyber_ninja', 'admin': False},
            {'username': 'pixel_queen', 'email': 'queen@quizclash.gg', 'pass': 'demo123', 'avatar': 'pixel_queen', 'admin': False},
            {'username': 'neon_falcon', 'email': 'falcon@quizclash.gg', 'pass': 'demo123', 'avatar': 'neon_falcon', 'admin': False},
            {'username': 'shadow_knight', 'email': 'knight@quizclash.gg', 'pass': 'demo123', 'avatar': 'shadow_knight', 'admin': False},
        ]

        user_objs = {}
        for du in demo_users:
            u = User(
                username=du['username'],
                email=du['email'],
                avatar=du['avatar'],
                is_admin=du['admin'],
                is_guest=False
            )
            u.set_password(du['pass'])
            db.session.add(u)
            user_objs[du['username']] = u

        db.session.flush()

        # Seed realistic player statistics
        stats_data = {
            'cyber_ninja': {'games': 28, 'wins': 22, 'losses': 5, 'draws': 1, 'score': 18450, 'high': 890, 'streak': 6, 'max_s': 8, 'correct': 132, 'total': 140},
            'pixel_queen': {'games': 25, 'wins': 18, 'losses': 6, 'draws': 1, 'score': 15200, 'high': 820, 'streak': 3, 'max_s': 7, 'correct': 114, 'total': 125},
            'neon_falcon': {'games': 19, 'wins': 12, 'losses': 7, 'draws': 0, 'score': 10800, 'high': 750, 'streak': 2, 'max_s': 5, 'correct': 82, 'total': 95},
            'shadow_knight': {'games': 14, 'wins': 8, 'losses': 6, 'draws': 0, 'score': 6950, 'high': 680, 'streak': 1, 'max_s': 4, 'correct': 55, 'total': 70},
            'admin': {'games': 10, 'wins': 7, 'losses': 3, 'draws': 0, 'score': 5400, 'high': 620, 'streak': 2, 'max_s': 5, 'correct': 44, 'total': 50},
        }

        for uname, s in stats_data.items():
            u = user_objs.get(uname)
            if u:
                stat = PlayerStats(
                    user_id=u.id,
                    total_games=s['games'],
                    wins=s['wins'],
                    losses=s['losses'],
                    draws=s['draws'],
                    total_score=s['score'],
                    highest_score=s['high'],
                    current_streak=s['streak'],
                    max_streak=s['max_s'],
                    total_correct=s['correct'],
                    total_answered=s['total']
                )
                db.session.add(stat)

                # Grant First Blood achievement
                if created_achievements.get('first_win') and s['wins'] >= 1:
                    ua = UserAchievement(user_id=u.id, achievement_id=created_achievements['first_win'].id)
                    db.session.add(ua)
                if created_achievements.get('quiz_master') and s['wins'] >= 5:
                    ua = UserAchievement(user_id=u.id, achievement_id=created_achievements['quiz_master'].id)
                    db.session.add(ua)

        db.session.flush()

        # Seed sample completed matches for landing page & recent match history
        match_samples = [
            {'mode': 'pvp', 'code': 'QC-7102', 'cat': cat_objs['python-programming'].id, 'diff': 'medium', 'q_count': 5, 'winner': user_objs['cyber_ninja'], 'loser': user_objs['pixel_queen'], 'w_score': 680, 'l_score': 540, 'days_ago': 1},
            {'mode': 'pvp', 'code': 'QC-8931', 'cat': cat_objs['cybersecurity'].id, 'diff': 'hard', 'q_count': 5, 'winner': user_objs['pixel_queen'], 'loser': user_objs['neon_falcon'], 'w_score': 710, 'l_score': 490, 'days_ago': 2},
            {'mode': 'pvp', 'code': 'QC-4419', 'cat': cat_objs['computer-science'].id, 'diff': 'medium', 'q_count': 5, 'winner': user_objs['cyber_ninja'], 'loser': user_objs['shadow_knight'], 'w_score': 650, 'l_score': 420, 'days_ago': 3},
        ]

        for ms in match_samples:
            match = MatchHistory(
                room_code=ms['code'],
                game_mode=ms['mode'],
                category_id=ms['cat'],
                difficulty=ms['diff'],
                total_questions=ms['q_count'],
                winner_id=ms['winner'].id,
                is_draw=False,
                played_at=datetime.now(timezone.utc) - timedelta(days=ms['days_ago'])
            )
            db.session.add(match)
            db.session.flush()

            p1 = MatchParticipant(
                match_id=match.id,
                user_id=ms['winner'].id,
                final_score=ms['w_score'],
                rank=1,
                correct_count=5,
                total_answered=5,
                avg_response_time=2.3
            )
            p2 = MatchParticipant(
                match_id=match.id,
                user_id=ms['loser'].id,
                final_score=ms['l_score'],
                rank=2,
                correct_count=4,
                total_answered=5,
                avg_response_time=3.8
            )
            db.session.add_all([p1, p2])

        db.session.commit()
        print(f"[Seed] Successfully seeded {len(raw_questions)} questions, {len(categories_data)} categories, and {len(demo_users)} demo users!")
