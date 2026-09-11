"""Seeds standard placement subject questions into CogniTree SQLite DB.
Subjects:
1. Data Structures & Algorithms (CLRS)
2. Computer Networks (Kurose & Ross)
3. Database Management Systems (Korth)
4. Operating Systems (Galvin)
5. Object-Oriented Programming (GoF)
"""

import sys
from pathlib import Path

# Add backend dir to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from core.database import SessionLocal, Base, engine
from core.models import Question, SkillType, Response, QuizSession

PLACEMENT_QUESTIONS = [
    # ==========================================
    # 1. DATA STRUCTURES & ALGORITHMS (CLRS)
    # ==========================================
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Binary Search Trees & AVL Balance",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "In an AVL tree, what is the maximum allowed difference between the heights of the left and right subtrees for any node?",
        "options": ["1", "0", "2", "log(n)"],
        "answer_index": 0,
        "explanation": "An AVL tree strictly enforces a balance factor of -1, 0, or +1 at every node, meaning height difference must be at most 1.",
    },
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Binary Search Trees & AVL Balance",
        "skill_type": SkillType.APPLICATION,
        "question_text": "Suppose keys [10, 20, 30] are inserted sequentially into an empty AVL tree. Which specific rotation is triggered to restore balance?",
        "options": [
            "Single Left (LL) Rotation at node 10",
            "Right-Left (RL) Double Rotation",
            "Single Right (RR) Rotation at node 30",
            "Left-Right (LR) Double Rotation",
        ],
        "answer_index": 0,
        "explanation": "Sequential ascending insertion creates a right-skewed imbalance (Right-Right condition), which is corrected by a single Left rotation at the unbalanced root (10), making 20 the new root.",
    },
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Graph Algorithms & Shortest Path",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "What is the time complexity of Dijkstra's algorithm implemented with a Min-Heap (Binary Heap) for a graph with V vertices and E edges?",
        "options": ["O((V + E) log V)", "O(V^2)", "O(V * E)", "O(E log E + V)"],
        "answer_index": 0,
        "explanation": "Using a binary min-heap / priority queue, Dijkstra's algorithm runs in O((V + E) log V) because each vertex extraction takes O(log V) and edge relaxations take O(E log V).",
    },
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Graph Algorithms & Shortest Path",
        "skill_type": SkillType.APPLICATION,
        "question_text": "Why does standard Dijkstra's algorithm fail on graphs containing negative edge weights, whereas Bellman-Ford succeeds?",
        "options": [
            "Dijkstra greedily assumes once a vertex is marked visited, its computed distance is permanently optimal, which negative edges can violate.",
            "Dijkstra requires undirected planar graphs only.",
            "Binary heaps cannot store negative key values.",
            "Dijkstra creates infinite loops on acyclic graphs.",
        ],
        "answer_index": 0,
        "explanation": "Dijkstra is a greedy algorithm that locks in the shortest distance upon popping a node. A negative edge encountered later could provide a shorter path to an already processed node, violating this greedy invariant.",
    },
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Dynamic Programming & Optimization",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "What are the two fundamental properties a computational problem must possess to be solved efficiently using Dynamic Programming?",
        "options": [
            "Optimal Substructure and Overlapping Subproblems",
            "Greedy Choice Property and Linearity",
            "Associativity and Commutativity",
            "Divide and Conquer with Disjoint Subproblems",
        ],
        "answer_index": 0,
        "explanation": "Dynamic Programming requires Overlapping Subproblems (subproblems are computed repeatedly) and Optimal Substructure (an optimal solution to the problem contains optimal solutions to subproblems).",
    },
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Dynamic Programming & Optimization",
        "skill_type": SkillType.APPLICATION,
        "question_text": "In the 0/1 Knapsack problem with capacity W and N items, what is the time and space complexity of the standard dynamic programming table approach?",
        "options": [
            "O(N * W) pseudo-polynomial time and O(N * W) space (optimizable to O(W))",
            "O(2^N) polynomial time and O(N) space",
            "O(N log W) time and O(W) space",
            "O(N + W) linear time and O(N) space",
        ],
        "answer_index": 0,
        "explanation": "0/1 Knapsack DP builds an (N+1) x (W+1) matrix, requiring O(N*W) time. Because row i only depends on row i-1, space can be optimized to a 1D array of size O(W).",
    },
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Heaps & Sorting Complexity",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "What is the worst-case time complexity of standard QuickSort, and when does it occur with a naive first-element pivot selection?",
        "options": [
            "O(N^2) when the array is already sorted or reverse-sorted",
            "O(N log N) regardless of input ordering",
            "O(N) when all elements are identical",
            "O(N log^2 N) when partitioned symmetrically",
        ],
        "answer_index": 0,
        "explanation": "With first-element pivot selection, sorted/reverse-sorted inputs produce maximally unbalanced partitions of size 0 and N-1 at every recursive level, degrading performance to O(N^2).",
    },
    {
        "topic": "Data Structures & Algorithms",
        "subtopic": "Heaps & Sorting Complexity",
        "skill_type": SkillType.APPLICATION,
        "question_text": "You need to continuously find the median of a dynamic stream of incoming numbers. What data structure combination provides O(log N) insertion and O(1) median query?",
        "options": [
            "Two heaps: a Max-Heap for the smaller half and a Min-Heap for the larger half",
            "A single balanced Binary Search Tree with linear pointer updates",
            "A circular doubly linked list with two middle pointers",
            "A monotone queue paired with an inverted hash map",
        ],
        "answer_index": 0,
        "explanation": "Maintaining a Max-Heap for the lower half and a Min-Heap for the upper half (balanced within size difference <= 1) allows O(log N) insertion and O(1) retrieval of the top root(s) for the median.",
    },

    # ==========================================
    # 2. COMPUTER NETWORKS (Kurose & Ross)
    # ==========================================
    {
        "topic": "Computer Networks",
        "subtopic": "OSI & TCP/IP Architecture",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "Which layer of the OSI model is responsible for end-to-end process-to-process communication, segmentation, and flow control?",
        "options": ["Transport Layer", "Network Layer", "Data Link Layer", "Session Layer"],
        "answer_index": 0,
        "explanation": "The Transport Layer (Layer 4) handles process-to-process communication using port numbers, packet segmentation, reliability, and flow control (e.g., TCP/UDP).",
    },
    {
        "topic": "Computer Networks",
        "subtopic": "OSI & TCP/IP Architecture",
        "skill_type": SkillType.APPLICATION,
        "question_text": "A client sends an HTTP GET request to a web server. At which layer are port numbers (e.g., source: 54321, dest: 80) encapsulated into the header?",
        "options": ["Transport Layer (TCP Segment)", "Network Layer (IP Packet)", "Data Link Layer (Ethernet Frame)", "Application Layer (HTTP Payload)"],
        "answer_index": 0,
        "explanation": "Source and destination port numbers are transport layer identifiers encapsulated in TCP/UDP segment headers before passing to the Network Layer for IP addressing.",
    },
    {
        "topic": "Computer Networks",
        "subtopic": "TCP Handshake & Congestion Control",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "What is the correct sequence of TCP flag packets exchanged during a standard three-way connection establishment handshake?",
        "options": [
            "SYN -> SYN-ACK -> ACK",
            "SYN -> ACK -> SYN-ACK",
            "FIN -> ACK -> FIN-ACK",
            "RST -> SYN -> ACK",
        ],
        "answer_index": 0,
        "explanation": "TCP 3-way handshake begins with client sending SYN, server replying with SYN-ACK, and client concluding with ACK to establish synchronous sequence numbers.",
    },
    {
        "topic": "Computer Networks",
        "subtopic": "TCP Handshake & Congestion Control",
        "skill_type": SkillType.APPLICATION,
        "question_text": "During TCP Tahoe congestion control, if a timeout packet loss occurs when the Congestion Window (cwnd) is 32 MSS, what happens to ssthresh and cwnd?",
        "options": [
            "ssthresh becomes 16 MSS, cwnd resets to 1 MSS (entering Slow Start)",
            "ssthresh remains 32 MSS, cwnd reduces by half to 16 MSS",
            "cwnd drops to 0 MSS and halts transmission entirely",
            "ssthresh is set to 1 MSS and cwnd enters Congestion Avoidance",
        ],
        "answer_index": 0,
        "explanation": "Upon timeout in TCP Tahoe, the slow start threshold (ssthresh) is set to half of the current cwnd (32/2 = 16 MSS), and cwnd resets to 1 MSS to re-enter slow start.",
    },
    {
        "topic": "Computer Networks",
        "subtopic": "IP Addressing & Subnetting",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "In CIDR notation, what is the default subnet mask and total usable host addresses for a /24 network prefix?",
        "options": [
            "Subnet Mask: 255.255.255.0, Usable Hosts: 254 (2^8 - 2)",
            "Subnet Mask: 255.255.0.0, Usable Hosts: 65534",
            "Subnet Mask: 255.255.255.128, Usable Hosts: 126",
            "Subnet Mask: 255.255.255.255, Usable Hosts: 256",
        ],
        "answer_index": 0,
        "explanation": "A /24 subnet has 24 network bits and 8 host bits. Total IPs = 2^8 = 256. Excluding the network ID (all 0s) and broadcast address (all 1s) leaves 254 usable hosts.",
    },
    {
        "topic": "Computer Networks",
        "subtopic": "IP Addressing & Subnetting",
        "skill_type": SkillType.APPLICATION,
        "question_text": "Given the IP address 192.168.10.68 with subnet mask 255.255.255.224 (/27), what is the broadcast address of this subnet?",
        "options": ["192.168.10.95", "192.168.10.63", "192.168.10.127", "192.168.10.255"],
        "answer_index": 0,
        "explanation": "Subnet mask .224 has block size 256 - 224 = 32. Subnet blocks are 0-31, 32-63, 64-95. The IP 68 falls in block 64-95. The network address is 192.168.10.64 and broadcast address is 192.168.10.95.",
    },
    {
        "topic": "Computer Networks",
        "subtopic": "Application Protocols: DNS & HTTP",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "Which DNS record type maps a domain hostname directly to its corresponding IPv4 address?",
        "options": ["A Record", "AAAA Record", "CNAME Record", "MX Record"],
        "answer_index": 0,
        "explanation": "'A' (Address) record maps a hostname to a 32-bit IPv4 address. 'AAAA' maps to IPv6, 'CNAME' aliases one name to another, and 'MX' specifies mail exchange servers.",
    },
    {
        "topic": "Computer Networks",
        "subtopic": "Application Protocols: DNS & HTTP",
        "skill_type": SkillType.APPLICATION,
        "question_text": "What is the key difference between HTTP/1.1 with Pipelining and HTTP/2 Multiplexing over a single TCP connection?",
        "options": [
            "HTTP/2 splits requests into independent binary frames, eliminating Head-of-Line (HoL) blocking at the application layer.",
            "HTTP/1.1 uses UDP while HTTP/2 uses TCP.",
            "HTTP/2 opens a new TCP connection for every parallel image asset.",
            "HTTP/1.1 encrypts headers automatically using TLS 1.3.",
        ],
        "answer_index": 0,
        "explanation": "HTTP/2 introduces binary framing and stream multiplexing, allowing multiple bidirectional request/response streams interleaved over one TCP connection without waiting for prior responses (solving application HoL blocking).",
    },

    # ==========================================
    # 3. DATABASE MANAGEMENT SYSTEMS (Korth)
    # ==========================================
    {
        "topic": "Database Management Systems",
        "subtopic": "ACID Properties & Transactions",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "In the ACID transactional model, which property guarantees that database changes made by committed transactions persist even during power crashes or system failures?",
        "options": ["Durability", "Atomicity", "Consistency", "Isolation"],
        "answer_index": 0,
        "explanation": "Durability ensures that once a transaction commits, its state modifications are permanently recorded in non-volatile storage (via write-ahead logging/WAL) and survive system crashes.",
    },
    {
        "topic": "Database Management Systems",
        "subtopic": "ACID Properties & Transactions",
        "skill_type": SkillType.APPLICATION,
        "question_text": "Transaction T1 reads row A, then Transaction T2 updates row A and commits. T1 reads row A again and sees different values. Which isolation phenomenon occurred?",
        "options": ["Non-Repeatable Read (Fuzzy Read)", "Dirty Read", "Phantom Read", "Lost Update"],
        "answer_index": 0,
        "explanation": "A Non-Repeatable Read occurs when a transaction reads the same existing row twice under Read Committed isolation and discovers altered values because another transaction modified and committed that row in the interim.",
    },
    {
        "topic": "Database Management Systems",
        "subtopic": "Relational Normalization (1NF to BCNF)",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "A relational schema is in Third Normal Form (3NF) if it is in 2NF and contains no:",
        "options": [
            "Transitive dependencies of non-prime attributes on candidate keys",
            "Partial dependencies on a composite primary key",
            "Multi-valued attributes or repeating groups",
            "Trivial functional dependencies",
        ],
        "answer_index": 0,
        "explanation": "3NF eliminates transitive dependencies (X -> Y and Y -> Z where Z is non-prime). Every non-key attribute must depend directly on the primary key, the whole key, and nothing but the key.",
    },
    {
        "topic": "Database Management Systems",
        "subtopic": "Relational Normalization (1NF to BCNF)",
        "skill_type": SkillType.APPLICATION,
        "question_text": "Given relation R(A, B, C, D) with candidate key {A, B} and Functional Dependencies: {AB -> CD, C -> D}. What highest normal form does R satisfy?",
        "options": ["2NF (violates 3NF because D transitively depends on AB via C)", "3NF", "BCNF", "1NF only"],
        "answer_index": 0,
        "explanation": "All non-prime attributes {C, D} are fully functionally dependent on candidate key {AB} (so it is 2NF). However, C -> D is a dependency between non-prime attributes, introducing a transitive dependency that violates 3NF.",
    },
    {
        "topic": "Database Management Systems",
        "subtopic": "Indexing & B+ Trees",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "Why are B+ Trees preferred over standard Binary Search Trees and B-Trees for database table indexing on disk storage?",
        "options": [
            "B+ Tree leaf nodes form a contiguous linked list for fast range queries, and internal nodes store only routing keys for high branching factor.",
            "B+ Trees have O(1) worst-case search complexity on unstructured blobs.",
            "B+ Trees consume zero disk memory when unindexed.",
            "B+ Trees prevent concurrent transaction locking completely.",
        ],
        "answer_index": 0,
        "explanation": "B+ Trees store all actual data records in linked leaf nodes (enabling high-throughput sequential range scans) while internal nodes fit many index keys per disk block (high fanout reduces disk I/O depth).",
    },
    {
        "topic": "Database Management Systems",
        "subtopic": "Indexing & B+ Trees",
        "skill_type": SkillType.APPLICATION,
        "question_text": "A table has a composite index on (department_id, hire_date, salary). Which of the following SQL WHERE clauses can fully utilize this index based on the leftmost prefix rule?",
        "options": [
            "WHERE department_id = 5 AND hire_date >= '2023-01-01'",
            "WHERE hire_date >= '2023-01-01' AND salary > 50000",
            "WHERE salary > 50000",
            "WHERE hire_date = '2023-01-01'",
        ],
        "answer_index": 0,
        "explanation": "According to the leftmost prefix rule for composite B-Tree indexes, queries must filter on leading columns (department_id) in sequence. Queries omitting department_id cannot use the index tree traversal.",
    },
    {
        "topic": "Database Management Systems",
        "subtopic": "SQL & Complex Joins",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "What is the primary difference between WHERE and HAVING clauses in SQL?",
        "options": [
            "WHERE filters individual rows before aggregation; HAVING filters aggregated groups after GROUP BY.",
            "WHERE is only used with subqueries; HAVING is used with JOINs.",
            "WHERE cannot compare integer values; HAVING can.",
            "WHERE operates after ORDER BY executes.",
        ],
        "answer_index": 0,
        "explanation": "The WHERE clause filters individual records prior to grouping. The HAVING clause filters grouped summary rows created by GROUP BY and aggregate functions like COUNT(), SUM(), AVG().",
    },
    {
        "topic": "Database Management Systems",
        "subtopic": "SQL & Complex Joins",
        "skill_type": SkillType.APPLICATION,
        "question_text": "What does a LEFT OUTER JOIN between Table A (5 rows) and Table B (3 matching rows, 2 non-matching) return?",
        "options": [
            "All 5 rows from Table A, with NULL populated for Table B columns where no match exists.",
            "Only the 3 matched rows from both tables.",
            "Exactly 15 rows from the Cartesian cross product.",
            "Only the unmatched rows from Table B.",
        ],
        "answer_index": 0,
        "explanation": "A LEFT JOIN guarantees all rows from the left table (A) appear in the result set. If no corresponding match exists in the right table (B), NULL is substituted for B's columns.",
    },

    # ==========================================
    # 4. OPERATING SYSTEMS (Galvin / OSTEP)
    # ==========================================
    {
        "topic": "Operating Systems",
        "subtopic": "Process Management & CPU Scheduling",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "What data structure does the operating system kernel maintain to preserve the state, program counter, registers, and memory mappings of an active process?",
        "options": ["Process Control Block (PCB)", "File Allocation Table (FAT)", "Translation Lookaside Buffer (TLB)", "Interrupt Vector Table (IVT)"],
        "answer_index": 0,
        "explanation": "The Process Control Block (PCB) is the kernel data structure containing PID, register context, CPU scheduling info, memory limits, and open file descriptors for a process.",
    },
    {
        "topic": "Operating Systems",
        "subtopic": "Process Management & CPU Scheduling",
        "skill_type": SkillType.APPLICATION,
        "question_text": "Processes P1 (Burst: 6ms), P2 (Burst: 8ms), P3 (Burst: 2ms) arrive at time t=0. Under Shortest Job First (SJF) non-preemptive scheduling, what is the average waiting time?",
        "options": ["3.0 ms (P3 waits 0ms, P1 waits 2ms, P2 waits 8ms -> (0+2+8)/3 = 3.33ms ≈ 3.33ms)", "7.0 ms", "5.5 ms", "1.5 ms"],
        "answer_index": 0,
        "explanation": "Execution order is P3 (0 to 2ms), then P1 (2 to 8ms), then P2 (8 to 16ms). Waiting times: P3=0, P1=2, P2=8. Average waiting time = (0 + 2 + 8) / 3 = 3.33 ms.",
    },
    {
        "topic": "Operating Systems",
        "subtopic": "Synchronization & Concurrency",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "What are the three mandatory requirements that any valid solution to the Critical Section Problem must satisfy?",
        "options": [
            "Mutual Exclusion, Progress, and Bounded Waiting",
            "Atomicity, Consistency, and Durability",
            "Preemption, Hold and Wait, and Circular Wait",
            "Paging, Segmentation, and Thrashing",
        ],
        "answer_index": 0,
        "explanation": "Classic Critical Section solutions must ensure: 1) Mutual Exclusion (only 1 thread in CS), 2) Progress (selection cannot be postponed indefinitely), and 3) Bounded Waiting (limit on entry turns).",
    },
    {
        "topic": "Operating Systems",
        "subtopic": "Synchronization & Concurrency",
        "skill_type": SkillType.APPLICATION,
        "question_text": "A counting semaphore S is initialized to 7. Then 12 wait() (P) operations and 8 signal() (V) operations are executed on S. What is the final value of S?",
        "options": ["3", "5", "-5", "11"],
        "answer_index": 0,
        "explanation": "Initial value = 7. Each wait() decrements S by 1 (12 operations = -12). Each signal() increments S by 1 (8 operations = +8). Final value = 7 - 12 + 8 = 3.",
    },
    {
        "topic": "Operating Systems",
        "subtopic": "Deadlock Characterization & Avoidance",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "Which algorithm is utilized by operating systems for deadlock avoidance by verifying whether granting a resource request leaves the system in a safe state?",
        "options": ["Banker's Algorithm", "Peterson's Algorithm", "Kruskal's Algorithm", "Lamport's Bakery Algorithm"],
        "answer_index": 0,
        "explanation": "Dijkstra's Banker's Algorithm simulates resource allocation to ensure at least one safe execution sequence exists where all processes can complete without deadlock.",
    },
    {
        "topic": "Operating Systems",
        "subtopic": "Deadlock Characterization & Avoidance",
        "skill_type": SkillType.APPLICATION,
        "question_text": "Which of Coffman's four deadlock conditions is effectively prevented if the OS forces processes to request all required resources at once prior to starting?",
        "options": ["Hold and Wait", "Mutual Exclusion", "Circular Wait", "No Preemption"],
        "answer_index": 0,
        "explanation": "Requiring a process to request and be allocated all its resources before execution begins guarantees it never holds allocated resources while waiting for additional ones, eliminating Hold and Wait.",
    },
    {
        "topic": "Operating Systems",
        "subtopic": "Virtual Memory & Page Replacement",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "What phenomenon occurs in virtual memory when an over-committed system spends more CPU time swapping pages in/out of secondary storage than executing actual code?",
        "options": ["Thrashing", "Internal Fragmentation", "Belady's Anomaly", "Starvation"],
        "answer_index": 0,
        "explanation": "Thrashing happens when the working sets of active processes exceed available physical memory frames, resulting in continuous page faults and near-zero CPU throughput.",
    },
    {
        "topic": "Operating Systems",
        "subtopic": "Virtual Memory & Page Replacement",
        "skill_type": SkillType.APPLICATION,
        "question_text": "What is Belady's Anomaly in operating systems page replacement?",
        "options": [
            "Under FIFO replacement, allocating more physical page frames can paradoxically increase the number of page faults.",
            "LRU replacement produces infinite page faults on recursive algorithms.",
            "Optimal page replacement requires exponential time complexity.",
            "Virtual addresses exceed physical address bus width.",
        ],
        "answer_index": 0,
        "explanation": "Belady's Anomaly proves that for certain FIFO page reference strings, increasing the number of physical page frames results in more total page faults rather than fewer.",
    },

    # ==========================================
    # 5. OBJECT-ORIENTED PROGRAMMING (GoF / Head First)
    # ==========================================
    {
        "topic": "Object-Oriented Programming",
        "subtopic": "Core Pillars & Abstraction",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "Which OOP concept bundles internal data and methods into a single unit while restricting direct external access via private/protected access modifiers?",
        "options": ["Encapsulation", "Polymorphism", "Dynamic Dispatch", "Multiple Inheritance"],
        "answer_index": 0,
        "explanation": "Encapsulation hides the internal implementation details of an object and exposes a clean public interface via getters/setters/methods, protecting data integrity.",
    },
    {
        "topic": "Object-Oriented Programming",
        "subtopic": "Core Pillars & Abstraction",
        "skill_type": SkillType.APPLICATION,
        "question_text": "Why should a base class in C++ with virtual methods always declare a virtual destructor?",
        "options": [
            "To ensure deleting a derived object via a base class pointer invokes the derived destructor first, preventing resource and memory leaks.",
            "To allow the base class to be instantiated as an interface.",
            "To prevent derived classes from overriding protected member functions.",
            "To force static memory allocation at compile time.",
        ],
        "answer_index": 0,
        "explanation": "Without a virtual destructor, deleting a derived instance through a base pointer causes undefined behavior where only the base destructor runs, leaking derived member resources.",
    },
    {
        "topic": "Object-Oriented Programming",
        "subtopic": "Polymorphism: Static vs Dynamic",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "Method Overloading is an example of which type of polymorphism?",
        "options": [
            "Compile-Time (Static) Polymorphism",
            "Runtime (Dynamic) Polymorphism",
            "Subtype Polymorphism via VTables",
            "Structural Duck Typing",
        ],
        "answer_index": 0,
        "explanation": "Method Overloading (same method name, different parameter signatures) is resolved at compile time based on static types, making it static/compile-time polymorphism.",
    },
    {
        "topic": "Object-Oriented Programming",
        "subtopic": "Polymorphism: Static vs Dynamic",
        "skill_type": SkillType.APPLICATION,
        "question_text": "How does the runtime engine execute dynamic method dispatch when calling a virtual method through a base reference?",
        "options": [
            "It looks up the function pointer inside the object's Virtual Method Table (vtable) indexed at runtime.",
            "It re-compiles the method bytecode in the local thread stack.",
            "It searches all subclasses linearly by string name.",
            "It serializes the object state to heap memory.",
        ],
        "answer_index": 0,
        "explanation": "Dynamic dispatch relies on a Virtual Table (vtable) associated with the class and a hidden vptr in each object pointing to the resolved virtual function implementation.",
    },
    {
        "topic": "Object-Oriented Programming",
        "subtopic": "SOLID Principles",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "Which SOLID principle states that derived classes must be completely substitutable for their base classes without altering program correctness?",
        "options": [
            "Liskov Substitution Principle (LSP)",
            "Single Responsibility Principle (SRP)",
            "Interface Segregation Principle (ISP)",
            "Dependency Inversion Principle (DIP)",
        ],
        "answer_index": 0,
        "explanation": "The Liskov Substitution Principle (LSP) mandates that objects of a superclass should be replaceable with objects of its subclasses without breaking application behavior.",
    },
    {
        "topic": "Object-Oriented Programming",
        "subtopic": "SOLID Principles",
        "skill_type": SkillType.APPLICATION,
        "question_text": "A class 'ReportManager' handles generating PDF reports, querying SQL tables, and sending notification emails. Which SOLID principle is primarily violated?",
        "options": [
            "Single Responsibility Principle (SRP - a class should have only one reason to change)",
            "Open/Closed Principle",
            "Liskov Substitution Principle",
            "Interface Segregation Principle",
        ],
        "answer_index": 0,
        "explanation": "ReportManager has multiple unrelated responsibilities (business formatting, DB access, email delivery). SRP states a class should encapsulate one cohesive responsibility with one reason to change.",
    },
    {
        "topic": "Object-Oriented Programming",
        "subtopic": "GoF Design Patterns",
        "skill_type": SkillType.MEMORIZATION,
        "question_text": "Which Creational Design Pattern guarantees that a class has only one single global instance while providing a global access point to it?",
        "options": ["Singleton Pattern", "Factory Method Pattern", "Prototype Pattern", "Builder Pattern"],
        "answer_index": 0,
        "explanation": "The Singleton Pattern restricts class instantiation to a single object with a private constructor and a static `getInstance()` method.",
    },
    {
        "topic": "Object-Oriented Programming",
        "subtopic": "GoF Design Patterns",
        "skill_type": SkillType.APPLICATION,
        "question_text": "You are designing an event-driven stock trading dashboard where multiple UI widgets need to be notified automatically when stock prices change. Which pattern is optimal?",
        "options": [
            "Observer Pattern (Publish/Subscribe)",
            "Decorator Pattern",
            "Adapter Pattern",
            "Flyweight Pattern",
        ],
        "answer_index": 0,
        "explanation": "The Observer Pattern defines a one-to-many dependency between objects so that when one subject changes state, all registered observers are notified and updated automatically.",
    },
]


def seed_database():
    """Wipes old chemistry/thermodynamics questions and loads standard placement questions."""
    db = SessionLocal()
    try:
        print("1. Cleaning up legacy questions (Chemistry, Thermodynamics, Cell Biology, Calculus)...")
        # Remove legacy responses & questions
        legacy_topics = ["Thermodynamics", "Organic Chemistry", "Cell Biology", "Calculus"]
        for topic in legacy_topics:
            legacy_questions = db.query(Question).filter(Question.topic == topic).all()
            for q in legacy_questions:
                db.query(Response).filter(Response.question_id == q.id).delete()
                db.delete(q)
        db.commit()

        # Check existing questions to avoid duplicates
        existing_texts = {q.question_text for q in db.query(Question).all()}

        inserted_count = 0
        for item in PLACEMENT_QUESTIONS:
            if item["question_text"] not in existing_texts:
                question = Question(
                    topic=item["topic"],
                    subtopic=item["subtopic"],
                    skill_type=item["skill_type"],
                    question_text=item["question_text"],
                    options=item["options"],
                    answer_index=item["answer_index"],
                    explanation=item["explanation"],
                    source_document_id=None,
                )
                db.add(question)
                inserted_count += 1

        db.commit()
        print(f"2. Successfully seeded {inserted_count} placement questions across 5 core topics.")

        # Print summary by topic
        rows = db.query(Question.topic, Question.skill_type).all()
        summary = {}
        for t, s in rows:
            skill = s.value if hasattr(s, "value") else str(s)
            summary.setdefault(t, {})[skill] = summary.setdefault(t, {}).get(skill, 0) + 1

        print("\nCurrent Question Bank Summary:")
        for topic, counts in summary.items():
            print(f"  • {topic}: {counts}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
