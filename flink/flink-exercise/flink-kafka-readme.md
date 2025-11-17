# Apache Flink and Kafka Integration Exercise

A hands-on guide to using Apache Flink SQL with Apache Kafka, exploring stream processing, storage separation, and changelog streams.

## Overview

This exercise demonstrates how Apache Flink processes data from Kafka topics using two distinct connectors: `kafka` (append-only) and `upsert-kafka` (updating streams). You'll learn how Flink separates stream processing from stream storage and how to work with changelog streams.

**Duration:** ~20 minutes

## Prerequisites

- Docker and Docker Compose installed
- Flink docker-based environment set up (see Docker Setup exercise)
- Basic understanding of SQL and streaming concepts
- Two terminal windows (one for SQL Client, one for kcat)

## What You'll Learn

- How Flink tables map to Kafka topics
- The difference between append and update streams
- Using the `kafka` connector for append-only streams
- Using the `upsert-kafka` connector for updating streams
- Working with different data formats (JSON, raw)
- Understanding changelog operations (+I, -U, +U)

## Key Concepts

### Tables in Flink SQL

In Flink SQL, a **table** is metadata describing how to interpret external storage as a SQL table. It's essentially a view onto a data stream stored outside of Flink (like a Kafka topic).

### Two Kafka Connectors

- **kafka**: Interprets topics as append-only streams (insert-only)
- **upsert-kafka**: Interprets topics as updating streams (supports updates/deletes based on primary key)

## Exercise Steps

### Setup

Start the Flink SQL Client in your first terminal:

```bash
docker compose run sql-client
```

Keep this terminal open for all SQL commands below.

---

### Part 1: Understanding Tables and Topics

#### 1. Create an Append-Only Table

Create a table backed by a Kafka topic named `append`:

```sql
CREATE TABLE json_table (
    `key` STRING,
    `value` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'append',
    'properties.bootstrap.servers' = 'broker:9092',
    'format' = 'json',
    'scan.startup.mode' = 'earliest-offset'
);
```

#### 2. Verify Topic Creation

In a **second terminal**, check if the topic exists:

```bash
docker compose exec -it kcat kcat -b broker:9092 -L
```

At this point, the topic doesn't exist yet. Topics are created when data is first written (auto-creation is enabled).

#### 3. Insert Data

Back in the SQL Client:

```sql
INSERT INTO json_table VALUES ('foo','one'), ('foo', 'two');
```

#### 4. Query the Table

```sql
SELECT * FROM json_table;
```

Expected output:

```
----------------------------+----------------------------+
                        key |                      value |
----------------------------+----------------------------+
                        foo |                        one |
                        foo |                        two |
```

Press **Ctrl-C** to stop the query.

#### 5. Inspect the Kafka Topic Directly

In your second terminal, examine the raw Kafka data:

```bash
docker compose exec -it kcat kcat -b broker:9092 -C -t append -f '\n
\tKey (%K bytes): %k
\tValue (%S bytes): %s
\tPartition: %p
\tOffset: %o
\tTimestamp: %T
\tHeaders: %h
--\n'
```

---

### Part 2: Multiple Views on the Same Topic

#### 6. Create a Second Table with Different Format

Create another table mapped to the **same** Kafka topic but with a different format:

```sql
CREATE TABLE raw_table (
    `data` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'append',
    'properties.bootstrap.servers' = 'broker:9092',
    'format' = 'raw',
    'scan.startup.mode' = 'earliest-offset'
);
```

#### 7. Query the Raw Table

```sql
SELECT * FROM raw_table;
```

Expected output:

```
-----------------------------+
                        data |
-----------------------------+
 {"key":"foo","value":"one"} |
 {"key":"foo","value":"two"} |
```

**Key Insight**: The same Kafka topic can be interpreted differently depending on the table definition!

---

### Part 3: Changelog Streams and Updates

#### 8. Enable Changelog Display Mode

Configure the SQL Client to show changelog operations:

```sql
SET 'sql-client.execution.result-mode' = 'tableau';
```

#### 9. View Insert Operations

Query the original table again:

```sql
SELECT * FROM json_table;
```

Now you'll see the `+I` (INSERT) operation:

```
+----+----------------------------+----------------------------+
| op |                        key |                      value |
+----+----------------------------+----------------------------+
| +I |                        foo |                        one |
| +I |                        foo |                        two |
```

#### 10. Create an Updating Table

Create a table with a primary key using the `upsert-kafka` connector:

```sql
CREATE TABLE updating_table (
    `key` STRING PRIMARY KEY NOT ENFORCED,
    `value` STRING
) WITH (
    'connector' = 'upsert-kafka',
    'topic' = 'update',
    'properties.bootstrap.servers' = 'broker:9092',
    'key.format' = 'json',
    'value.format' = 'json'
);
```

#### 11. Insert Duplicate Keys

```sql
INSERT INTO updating_table VALUES ('foo','one'), ('foo', 'two');
```

#### 12. Observe Update Operations

```sql
SELECT * FROM updating_table;
```

Expected output:

```
+----+----------------------------+----------------------------+
| op |                        key |                      value |
+----+----------------------------+----------------------------+
| +I |                        foo |                        one |
| -U |                        foo |                        one |
| +U |                        foo |                        two |
```

**Understanding the Operations:**
- `+I`: INSERT (new record)
- `-U`: UPDATE_BEFORE (deletes old value)
- `+U`: UPDATE_AFTER (inserts new value)

#### 13. Return to Normal Display Mode

```sql
SET 'sql-client.execution.result-mode' = 'table';
```

---

## Changelog Operations Explained

| Operation | Symbol | Meaning |
|-----------|--------|---------|
| Insert | `+I` | New record added to stream |
| Update Before | `-U` | Old value being removed |
| Update After | `+U` | New value being inserted |
| Delete | `-D` | Record removed from stream |

## Connector Comparison

| Feature | kafka | upsert-kafka |
|---------|-------|--------------|
| Stream Type | Append-only | Updating |
| Primary Key | Not required | Required |
| Updates | Not supported | Supported |
| Deletes | Not supported | Supported |
| Use Case | Event logs, metrics | Database CDC, aggregations |

## Important Notes

### DataStream API vs Table API/SQL

- **Table API/SQL**: Designed for changelog streams (supports updates/deletes)
- **DataStream API**: Every stream is append-only

### Confluent Cloud Differences

In Confluent Cloud, Flink and Kafka are more tightly integrated. The separation between `kafka` and `upsert-kafka` connectors works differently. See the companion Confluent Cloud exercise for details.

## Supported Formats

Flink supports various data formats:

- **JSON**: Human-readable, schema embedded
- **Apache Avro**: Binary, schema separate
- **Confluent Avro**: Avro with Schema Registry integration
- **Protobuf**: Google's binary format
- **Debezium**: CDC format from databases
- **Raw**: Unstructured string data

## Troubleshooting

**Topic not created**: Make sure you've inserted data first. Topics auto-create on first write.

**Can't connect to broker**: Verify the broker is running with `docker compose ps`

**kcat not working**: Ensure you're using the second terminal and the container is running

**Query hangs**: Remember to press Ctrl-C to stop SELECT queries

## Experiments to Try

1. Insert more data with duplicate keys into `updating_table` and observe the changelog
2. Create tables with different formats on the same topic
3. Try using `DELETE` operations with `upsert-kafka`
4. Explore other Kafka connector properties like `scan.startup.mode`

## Next Steps

- Learn about streaming analytics and aggregations
- Explore event time processing and watermarks
- Study changelog processing in the Apache Flink SQL course
- Try the Confluent Cloud version of this exercise

## Resources

- [Apache Kafka SQL Connector Documentation](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/table/kafka/)
- [Upsert Kafka SQL Connector Documentation](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/table/upsert-kafka/)
- [JSON Format](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/table/formats/json/)
- [Avro Format](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/table/formats/avro/)
- [Confluent Avro Format](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/table/formats/avro-confluent/)

## Community

Join the **#developer-confluent-io** Slack channel for questions and discussions.

---

**Promo Codes**: Use `FLINK101` & `CONFLUENTDEV1` for $25 of free Confluent Cloud usage