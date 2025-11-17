# Apache Flink Web UI Exercise

A hands-on guide to using Flink's Web UI to monitor and debug streaming SQL queries.

## Overview

This exercise teaches you how to use Apache Flink's Web UI to inspect job execution, understand processing pipelines, and debug common issues in real-time streaming applications.

**Duration:** ~15 minutes

## Prerequisites

- Docker and Docker Compose installed
- Flink docker-based environment set up
- Basic understanding of SQL
- Web browser for accessing the UI

## What You'll Learn

- How to navigate the Flink Web UI
- Understanding job graphs and task structures
- Interpreting task-level metrics (backpressure, busyness, data skew)
- Reading execution plans with `EXPLAIN`
- Basic debugging techniques for streaming jobs

## Exercise Steps

### 1. Start the SQL Client

Open a terminal and run:

```bash
docker compose run sql-client
```

### 2. Create a Test Table

Create a table that generates fake page view data:

```sql
CREATE TABLE `pageviews` (
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

### 3. Start a Streaming Query

Execute an unbounded streaming query:

```sql
SELECT COUNT(*) FROM pageviews;
```

This query will continuously count incoming page views.

### 4. Explore the Web UI

Open your browser and navigate to:

```
http://localhost:8081
```

**Key areas to explore:**

- **Running Jobs**: Click on your query in the jobs list
- **Job Graph**: Visualize the processing pipeline with connected tasks
- **Task Metrics**: View backpressure, busyness, and data skew
- **I/O Metrics**: Check internal network communication between tasks
- **Subtask Details**: Click on tasks for per-subtask metrics

### 5. Understand the Job Graph

The job graph shows your processing pipeline with two main tasks:

1. **Source Task**: Reads data from the faker connector
2. **Aggregation Task**: Contains chained operators (GroupAggregate, ConstraintEnforcer, Sink)

### 6. Analyze Metrics

**Backpressure (max)**: Maximum percentage of time subtasks were blocked sending data downstream

**Busyness (max)**: Maximum percentage of time subtasks spent doing useful work

**Data Skew**: Variation in records processed per second across parallel subtasks
- 0% = perfectly balanced
- 100% = maximum imbalance

### 7. Stop and Explain the Query

Stop the running query in the SQL Client, then run:

```sql
EXPLAIN SELECT COUNT(*) FROM pageviews;
```

This shows the optimized execution plan that maps to what you saw in the job graph.

### 8. Explore System Components

In the Web UI sidebar, check out:

- **Job Manager**: Configuration, metrics, and logs
- **Task Managers**: Resource usage and task distribution

## Key Concepts

### Task Chaining

Multiple operators that are directly connected run together in the same thread within a subtask for efficiency. In this example, the GroupAggregate, ConstraintEnforcer, and Sink operators are chained together.

### Metric Aggregation

Task-level metrics report the worst-case (maximum) values across all parallel subtasks because one overwhelmed instance can degrade the entire cluster's performance.

### Exchange Boundaries

The `Exchange` in the execution plan creates boundaries between tasks in the job graph, indicating where data is shuffled between parallel subtasks.

## Common Debugging Scenarios

- **Data Skew**: Uneven distribution of work across subtasks
- **Idle Sources**: Sources not producing data
- **Backpressure**: Downstream tasks can't keep up with incoming data
- **Always Busy Tasks**: May indicate performance bottlenecks (except for certain connectors like faker)

## Next Steps

- Examine checkpoints and watermarks in later exercises
- Try modifying the query to see how the job graph changes
- Experiment with different table configurations
- Monitor how metrics change under different workloads

## Resources

- [Confluent Cloud Query Profiler](https://docs.confluent.io/cloud/current/flink/index.html) - Similar tool for cloud environments
- [Flink EXPLAIN Documentation](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/table/sql/explain/)
- [FLIP-418: Data Skew Calculation](https://cwiki.apache.org/confluence/display/FLINK/FLIP-418)

## Troubleshooting

**Can't access Web UI**: Ensure port 8081 is not blocked and the Flink cluster is running

**Query not appearing**: Wait a moment for the job to register, then refresh the page

**Docker issues**: Verify Docker Compose is running and containers are healthy

## Community

Join the **#developer-confluent-io** Slack channel for questions and discussions.

---

**Promo Codes**: Use `FLINK101` & `CONFLUENTDEV1` for $25 of free Confluent Cloud usage