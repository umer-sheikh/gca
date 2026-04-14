# Architecture Notes

## Design principle

The repository deliberately separates *schemas*, *services*, *tools*, and *runtime control* so that the LangChain-facing layer remains thin and the provider-specific logic stays testable.

## Layers

### 1. Contracts

`contracts/` contains the typed request and response schemas that mirror the paper's Table 4. Every tool input is represented as a Pydantic model, and every output inherits from a shared `ClimateToolOutput` with a `meta` field.

### 2. Core runtime

`core/` hosts shared runtime utilities:

- artifact persistence
- HTTP helpers with retries
- tracing
- statistical normalization
- JSON-safe serialization

### 3. Infrastructure adapters

`infra/` wraps external systems:

- Earth Engine
- Open-Meteo
- Tavily
- OpenAI Responses API
- BioCLIP CLI
- GCC carbon factor catalogs
- TensorFlow bird classifier

### 4. Tool layer

`tools/` exposes provider services through LangChain `StructuredTool` instances. Each tool wrapper validates typed inputs, invokes a service, normalizes metadata, and returns a serializable dictionary.

### 5. Agent runtime

`agent/runtime.py` implements a compact tool-calling loop:

1. infer dominant domain through the controller,
2. bind a minimal tool subset to the model,
3. iterate tool calls up to a maximum step count,
4. append observations as structured messages,
5. return a grounded answer plus the trace.

## Why artifact references exist

Satellite imagery and derived indices can be large. Passing entire arrays back through the LLM context would be wasteful and brittle. The runtime therefore persists arrays and preview images to the artifact store and lets downstream tools consume stable artifact references.

## Why the controller is heuristic

The attached paper presents a tool controller abstraction, but does not publish the learned router. This implementation therefore uses a transparent heuristic router that is easy to extend or replace.
