**Workflow**

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
        __start__([<p>__start__</p>]):::first
        generate(generate)
        evaluate(evaluate)
        optimize(optimize)
        __end__([<p>__end__</p>]):::last
        __start__ --> generate;
        evaluate -. &nbsp;approved&nbsp; .-> __end__;
        evaluate -. &nbsp;needs_improvement&nbsp; .-> optimize;
        generate --> evaluate;
        optimize --> evaluate;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
```

---



```cs
          +-----------+             
          | __start__ |             
          +-----------+             
                 *                  
                 *                  
                 *                  
           +----------+             
           | generate |             
           +----------+             
                 *                  
                 *                  
                 *                  
           +----------+             
           | evaluate |             
           +----------+             
          ...         ..            
         .              ..          
       ..                 .         
+---------+           +----------+  
| __end__ |           | optimize |  
+---------+           +----------+  
```