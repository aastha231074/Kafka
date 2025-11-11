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