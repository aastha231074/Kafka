# Batch and Stream Processing with Flink SQL

## Overview

This exercise introduces you to Apache Flink SQL by demonstrating the differences and similarities between batch and streaming execution modes. You'll work with both bounded and unbounded data sources to understand how Flink processes data in each mode.

**Duration:** ~15 minutes  
**Prerequisites:** Docker installation and basic SQL knowledge

## Learning Objectives

By completing this exercise, you will:
- Understand the difference between batch and streaming execution modes
- Learn how to switch between execution modes in Flink SQL
- Observe how Flink handles bounded vs unbounded data sources
- Experience real-time data processing with streaming mode
- Work with the flink-faker connector for generating mock data

## Prerequisites

Before starting this exercise, ensure you have:
1. Docker and Docker Compose installed on your system
2. Completed the Docker setup instructions for Apache Flink
3. Flink SQL Client running and accessible

## Exercise Steps

### 1. Create a Bounded Table

First, create a table with 500 rows of mock pageview data using the flink-faker connector:

```sql
CREATE TABLE `bounded_pageviews` (
  `url` STRING,
  `ts` TIMESTAMP(3)
)
WITH (
  'connector' = 'faker',
  'number-of-rows' = '500',
  'rows-per-second' = '100',
  'fields.url.expression' = '/#{GreekPhilosopher.name}.html',
  'fields.ts.expression' =  '#{date.past ''5'',''1'',''SECONDS''}'
);
```

**Optional:** View sample data with:
```sql
SELECT * FROM bounded_pageviews LIMIT 10;
```

### 2. Batch Mode with Bounded Input

Switch to batch execution mode:
```sql
SET 'execution.runtime-mode' = 'batch';
```

Run a counting query:
```sql
SELECT COUNT(*) AS `count` FROM bounded_pageviews;
```

**Expected Result:** A single final count of 500 (takes ~5 seconds)

### 3. Streaming Mode with Bounded Input

Switch to streaming mode:
```sql
SET 'execution.runtime-mode' = 'streaming';
```

Run the same query:
```sql
SELECT COUNT(*) AS `count` FROM bounded_pageviews;
```

**Expected Behavior:** The count increments from 100 → 200 → ... → 500

#### Enable Changelog Mode

To see the update stream more clearly:
```sql
SET 'sql-client.execution.result-mode' = 'changelog';
SELECT COUNT(*) AS `count` FROM bounded_pageviews;
```

**Expected Output:**
```
 op                count
 -----------------------
 -U                  497
 +U                  498
 -U                  498
 +U                  499
 -U                  499
 +U                  500
```

Where `-U` represents an update retraction and `+U` represents the new value.

### 4. Streaming Mode with Unbounded Input

Create an unbounded table (no row limit):
```sql
CREATE TABLE `streaming_pageviews` (
  `url` STRING,
  `ts` TIMESTAMP(3)
)
WITH (
  'connector' = 'faker',
  'rows-per-second' = '100',
  'fields.url.expression' = '/#{GreekPhilosopher.name}.html',
  'fields.ts.expression' =  '#{date.past ''5'',''1'',''SECONDS''}'
);
```

Reset to table display mode:
```sql
SET 'sql-client.execution.result-mode' = 'table';
```

Run the counting query:
```sql
SELECT COUNT(*) AS `count` FROM streaming_pageviews;
```

**Expected Behavior:** Count continues to increment indefinitely

#### Adjust Processing Speed

You can modify the data generation rate:
```sql
-- Slow down
ALTER TABLE `streaming_pageviews` SET ('rows-per-second' = '10');

-- Speed up
ALTER TABLE `streaming_pageviews` SET ('rows-per-second' = '1000');
```

## Key Concepts

### Batch vs Streaming Mode

| Aspect | Batch Mode | Streaming Mode |
|--------|-----------|----------------|
| Input | Bounded datasets | Bounded or unbounded streams |
| Results | Single final result | Continuous updates |
| Execution | Waits for all data | Processes as data arrives |
| Use Case | Historical analysis | Real-time analytics |

### Result Display Modes

- **Table Mode** (default): Updates values in place
- **Changelog Mode**: Shows the stream of update operations (-U, +U, +I, -D)

### The flink-faker Connector

A powerful tool for generating mock data with configurable:
- Row limits (`number-of-rows`)
- Generation rate (`rows-per-second`)
- Data patterns using Faker expressions

## Clean Up

### Exit Flink SQL Client
```sql
quit;
```

### Stop Docker Containers
```bash
docker compose down -v
```

This stops all containers and removes volumes used for checkpointing.

## Additional Resources

- [Flink SQL Client Documentation](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sqlclient/)
- [CREATE Statements](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/create/)
- [ALTER Statements](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/alter/)
- [flink-faker GitHub Repository](https://github.com/knaufk/flink-faker)

## Troubleshooting

**Query takes longer than expected:**
- Check the `rows-per-second` configuration
- Ensure Docker has sufficient resources allocated

**Connection issues:**
- Verify Docker containers are running: `docker ps`
- Check Flink cluster status in the Web UI (usually http://localhost:8081)

**Changelog mode not showing updates:**
- Ensure you're in streaming mode, not batch mode
- Verify the result-mode setting is 'changelog'

## Next Steps

Continue with the next exercises in the Apache Flink 101 course to learn about:
- The Flink Runtime architecture
- Using the Flink Web UI
- Integrating Flink with Apache Kafka
- Stateful stream processing
- Event time and watermarks

---