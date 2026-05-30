**Workflow**
```mermaid
graph TD
    A(START) --> B(Generate Outline)
    B --> C(Generate Bog)
    C --> D(END)
```

**State**
```
topic: str
outline: str
blog: str
```