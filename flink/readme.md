# Apache Flink 

## What is Apache Flink: 
- Flink is a framework for processing data streams in real time. Think of it as a powerful engine that can analyze and transform data as it flows through your system. 

## A Real-World Analogy
Imagine an e-commerce website:

- <b> Kafka </b>: Carries the stream of user clicks, purchases, and page views from your website to various systems
- <b> Flink </b>: Analyzes those clicks in real-time to detect patterns, calculate trending products, identify fraud, or trigger personalized recommendations

### They Often Work Together!
In many systems, Kafka and Flink are teammates:

- Kafka collects and transports the data streams
- Flink reads from Kafka, processes the data (filtering, joining, aggregating)
- Flink might write results back to Kafka or to a database
- So in summary: Kafka moves data, Flink transforms it.

## 4 Big Ideas of Apache Flink: 

### 1. Streaming: 
This is about processing data continuously as it arrives, not in batches. In technical terms, event streaming is the practice of capturing event in real time as they occur.

#### <b> Simple analogy: </b>
- Batch processing = Collecting all your emails for the day and reading them at 5 PM
- Stream processing = Reading and responding to emails the moment they arrive

Flink treats everything as an infinite stream of events. Even if you have a fixed dataset (like a database table), Flink can process it as a stream.

Stream processing is done in parallel by partitioning event streams into parallel sub-streams each of which can be independently processed. 

The partitioning into independently processed pipelines is crucial for scalability. These independent parallel operators share nothing and can run at full speed. 

#### <b> Think of it like a restaurant kitchen: </b>

Without parallelism: One chef handles all orders sequentially (slow!)

With parallelism:

- Incoming orders are divided among 4 chefs
- Each chef has their own station (shares nothing)
- Each works on their orders independently at full speed
- Much faster overall! </br>
In Flink, the "orders" are events, and the "chefs" are parallel operator instances.

#### <b> The 4 Data Distribution Patterns </b>
When data flows between operators in Flink, it needs to decide: "Which parallel instance should receive this event?" Here are the four main patterns:

#### 1. Forward
What it is: Events stay in the same partition - no shuffling at all.

When it happens: When the upstream and downstream operators have the same parallelism and you want to maintain locality.

Visual:
```bash
Operator A (Filter by shape)          Operator B (Resize)
   Instance 1: square images  ─────►  Instance 1: resizes those squares
   Instance 2: round images   ─────►  Instance 2: resizes those rounds
```

Key Points:
- Instance 1's output goes ONLY to Instance 1 of the next operator
- Instance 2's output goes ONLY to Instance 2 of the next operator
- They stay in their own pipeline/lane
- No mixing, no copying, no network shuffling
- Why it's fast: No data movement across the network!

#### 2. Parallel (Key-by / Hash Partitioning)
What it is: Events are distributed based on a key (like user ID, product ID). All events with the same key always go to the same instance.

Example:
- Processing user purchases
- Key = user_id
- All purchases from "User123" always go to the same instance
- That instance can maintain a counter for User123's total spending
- Why it matters: Essential for stateful operations! You need all events for the same key in one place to maintain accurate state.

Visual:
```bash
Operator A                     Operator B (grouped by key)
   All events  ─────►  hash(key) ─────►  Instance 1: keys [A, D, G]
                                         Instance 2: keys [B, E, H]
                                         Instance 3: keys [C, F, I]
```

##### Why Keep All Data for a User_ID in One Instance?
<b> The Problem: </b> Stateful Operations Need Co-location

Imagine you're tracking: "Total amount spent by each user"

❌ If user_123's events were scattered across instances:
```python
user_123 buys $50 headphones → Instance 1 (state: user_123 = $50)
user_123 buys $30 cable      → Instance 3 (state: user_123 = $30)
user_123 buys $20 adapter    → Instance 2 (state: user_123 = $20)

Query: "How much has user_123 spent?"
Answer: You'd have to ask all 3 instances and aggregate! 😰
```
<b> Problems: </b>
- Expensive coordination between instances
- Network overhead
- Slower processing
- Complex to implement correctly

✅ With KeyBy - all user_123 events go to Instance 1:
```python 
user_123 buys $50 headphones → Instance 1 (state: user_123 = $50)
user_123 buys $30 cable      → Instance 1 (state: user_123 = $80)
user_123 buys $20 adapter    → Instance 1 (state: user_123 = $100)

Query: "How much has user_123 spent?"
Answer: Ask Instance 1 only! Instant result: $100 ✅
```
<b> Benefits: </b>
- No coordination needed - each instance independently manages its users
- Fast lookups - state is local
- Simple to implement - just increment a counter
- No network shuffling during computation

##### The Data Skew Problem 
<b> The Scenario: </b>
```python
100 users distributed across 4 instances:

Instance 1: 25 normal users     → 100 events/sec
Instance 2: 25 normal users     → 100 events/sec  
Instance 3: 25 normal users     → 100 events/sec
Instance 4: 24 normal users     → 100 events/sec
            + 1 SUPER ACTIVE user → 10,000 events/sec ⚠️

Total: Instance 4 is processing 10,100 events/sec!
The others: only 100 events/sec
```
Result: Instance 4 is the bottleneck. The whole pipeline slows down!

#### 3. Repartition (Random Distribution)
What it is: Events are distributed randomly across all downstream instances. Each event has an equal chance of going anywhere.

Visual:

```python
Operator A                     Operator B
   Instance 1  ─┐
   Instance 2  ─┼──randomly──►  Instance 1
   Instance 3  ─┘    mix        Instance 2
                                 Instance 3
```

Example:

- You have 1000 images to process (resize, filter)
- Each image is independent
- Randomly distribute them to 10 worker instances
- Each worker processes ~100 images
- Why use it: When you want to shuffle data but don't care about any specific distribution pattern.

#### 4. Rebalance (Round-Robin Distribution)
What it is: Events are distributed evenly in a round-robin fashion. Much more balanced than random.

Visual:

```python 
Operator A                     Operator B
   Instance 1  ─┐              Instance 1 (gets 1st, 4th, 7th...)
   Instance 2  ─┼─round-robin─►Instance 2 (gets 2nd, 5th, 8th...)
   Instance 3  ─┘              Instance 3 (gets 3rd, 6th, 9th...)
```

Example:

- Data source reads 1000 records
- 4 downstream operators need to process them
- Rebalance ensures each gets exactly 250 records (or as close as possible)

<b> Why use it: </b>

- Load balancing - ensures even distribution
- Prevents one instance from being overwhelmed while others are idle
- Better than random when you have data skew

Comparison Table
| Pattern | Distribution | Use Case | Network Cost |
|-----------|-----------|-----------|-----------|
| Forward | Same partition	Same parallelism | maintain locality | None (best)|
| Parallel (KeyBy) | By hash of key | Stateful operations, grouping | Medium |
| Repartition	Random | Independent tasks | don't care about distribution | High |
| Rebalance | Round-robin | Load balancing, even distribution | High |

Real-World Example: E-commerce Pipeline
```python 
Web Clicks Stream (parallelism=2)
         │
         ├─[Forward]─► Parse Clicks (parallelism=2)
         │             (no reshuffling needed)
         │
         ├─[KeyBy user_id]─► Calculate User Sessions (parallelism=4)
         │                   (need all clicks per user together)
         │
         ├─[Rebalance]─► Enrich with Product Data (parallelism=8)
         │               (even load distribution)
         │
         └─[Repartition]─► Log to Storage (parallelism=3)
                           (any instance can write)
```
Key Takeaway
The choice of distribution pattern affects:

- Performance: Forward is fastest (no network), others require data shuffling
- Correctness: KeyBy is essential for stateful operations
- Load balancing: Rebalance ensures even work distribution


### 2. State
State is memory of the past - information that Flink remembers across multiple events.

#### Why it matters: Most real-world applications need to remember things!

#### <b> Examples: </b> 
- Counting: "How many purchases has this user made?" (you need to remember the count)
- Averages: "What's the average temperature over the last hour?" (you need to remember recent readings)
- Sessions: "Is this user still active?" (you need to remember when they last clicked)
Without state, every event would be processed in isolation with no context. State lets Flink be "smart" by remembering relevant information.

### 3. Time
Time is when things actually happened vs when Flink processes them.

#### This is trickier than it sounds! There are different notions of time:

- <b> Event Time: </b> When the event actually occurred in the real world

    Example: A sensor recorded temperature at 2:00 PM
- <b> Processing Time: </b> When Flink processes the event

    Example: Flink receives and processes that reading at 2:05 PM (5 minutes late!)
Why it matters:

<p> Network delays, system outages, or late-arriving data can cause events to arrive out of order
Flink handles this gracefully using "event time" - so even if data arrives late or shuffled, results are still correct
Example: If you're calculating "sales per hour," you want to group by when the sale actually happened, not when your system happened to process it.
</p>

### 4. Use of State Snapshots (Checkpointing)
This is about fault tolerance - making sure you don't lose progress if something crashes.

#### <b> How it works: </b>
Flink periodically takes "snapshots" of the entire application state (like saving your video game progress).
#### What happens when things go wrong:

❌ Server crashes <br>
✅ Flink restarts from the last snapshot <br>
✅ No data lost, processing continues exactly where it left off <br>
Simple analogy: Like auto-save in a document - if your computer crashes, you don't lose everything, just back to the last auto-save point.