# What is LangGraph?

- LangGraph is Orchestration framework building intelligent, stateful, and multi-step LLM workflows.

# LLM Workflow

## Prompt  Chaining
```mermaid
graph TD
    A(In) --> B(LLM Call 1)
    B --> |Output 1|C(Gate)
    C --> |Pass| D(LLM Call 2)
    C --> |Fail| E(Exit)
    D --> |Output 2| F(LLM Call 3)
    F --> Out

```


## Routing
```mermaid
graph TD
    A(In) --> B(LLM Call Router)
    B --> C(LLM Call 1)
    B --> E(LLM Call 2)
    B --> F(LLM Call 3)
    C --> D(Out)
    E --> D
    F --> D
```

## Parallelization
```mermaid
graph TD
    B(In) --> C(LLM Call 1)
    B --> E(LLM Call 2)
    B --> F(LLM Call 3)
    C --> D(Aggregator)
    E --> D
    F --> D
    D --> G(Out)
```

## Orchestrator Workflow
```mermaid
graph TD
    A(In) --> B(Orchestrator)
    B --> C(LLM Call 1)
    B --> E(LLM Call 2)
    B --> F(LLM Call 3)
    C --> D(Synthesizer)
    E --> D
    F --> D
    D --> G(Out)
```

## Evaluator Optimizer
```mermaid
graph TD
    A(In) --> B(LLM Call Generator)
    B --> |Solution|C(LLM Call Evaluator)
    C --> |Rejected + Feedback|B
    C --> |Accepted| F(Out)
```

---

**Few Topic need to know**
- Graphs, Nodes, Edges
- State
- Reducers


---

Sir Lecture: [YT](https://www.youtube.com/watch?v=D5KhiCDM9XQ&list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL&index=5)