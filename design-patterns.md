# Creational Design Patterns

## Singleton

### Problem
You need exactly one instance of a class shared across the entire system.
> Multiple instances cause inconsistencies, resource conflicts, or waste. Like a government—a country needs one official government, not several competing ones.

### Solution
Make the class responsible for creating and managing its single instance.
> Use a private constructor and static method to access the instance. The class controls when and how it's instantiated.

### Code Examples

#### Python
```python
class DatabaseConnection:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if not DatabaseConnection._initialized:
            self.host = "localhost"
            self.port = 5432
            self.connection = None
            DatabaseConnection._initialized = True
            print("Database connection created")
    
    def connect(self):
        if not self.connection:
            self.connection = f"Connected to {self.host}:{self.port}"
        return self.connection
    
    def query(self, sql):
        return f"Executing: {sql}"

# Usage - always returns same instance
db1 = DatabaseConnection()  # "Database connection created"
db2 = DatabaseConnection()  # (no message - same instance)

print(db1 is db2)  # True
db1.host = "192.168.1.100"
print(db2.host)    # "192.168.1.100" - same object
```

#### Rust
```rust
use std::sync::{Arc, Mutex, Once};

struct DatabaseConnection {
    host: String,
    port: u16,
    connection: Option<String>,
}

impl DatabaseConnection {
    fn instance() -> Arc<Mutex<DatabaseConnection>> {
        static mut INSTANCE: Option<Arc<Mutex<DatabaseConnection>>> = None;
        static ONCE: Once = Once::new();
        
        unsafe {
            ONCE.call_once(|| {
                let connection = DatabaseConnection {
                    host: "localhost".into(),
                    port: 5432,
                    connection: None,
                };
                INSTANCE = Some(Arc::new(Mutex::new(connection)));
                println!("Database connection created");
            });
            INSTANCE.clone().unwrap()
        }
    }
    
    fn connect(&mut self) -> String {
        if self.connection.is_none() {
            self.connection = Some(format!("Connected to {}:{}", self.host, self.port));
        }
        self.connection.clone().unwrap()
    }
    
    fn query(&self, sql: &str) -> String {
        format!("Executing: {}", sql)
    }
}

// Usage
let db1 = DatabaseConnection::instance();
let db2 = DatabaseConnection::instance();

// Same instance (same Arc pointer)
db1.lock().unwrap().host = "192.168.1.100".into();
println!("{}", db2.lock().unwrap().host);  // "192.168.1.100"
```

### Common Use Cases
**General:**
- Application configuration ensuring one settings object across the system
- Logging where all parts write to the same log
- Cache management with a single shared storage

**IoT/ML:**
- Hardware bus controllers since only one process can control I2C or SPI at a time
- Model registry providing centralized access to loaded models
- Telemetry aggregation collecting metrics from all device components

---

## Factory Method

### Problem
You need to create objects but don't know the exact type until runtime.
> Hardcoding object creation makes code rigid—adding new types requires modifying existing code everywhere. Like ordering "a vehicle" without specifying car, truck, or motorcycle until delivery.

### Solution
Define an interface for creating objects, but let subclasses decide which class to instantiate.
> The creator class works with the product interface, while concrete creators return specific implementations. Client code stays the same when new types are added.

### Code Examples

#### Python
```python
from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def read(self): pass

class FileSource(DataSource):
    def read(self):
        return "Reading from file..."

class DatabaseSource(DataSource):
    def read(self):
        return "Reading from database..."

class APISource(DataSource):
    def read(self):
        return "Reading from API..."

# Factory
class DataProcessor:
    def create_source(self, source_type: str) -> DataSource:
        if source_type == "file":
            return FileSource()
        elif source_type == "db":
            return DatabaseSource()
        elif source_type == "api":
            return APISource()
        raise ValueError(f"Unknown source: {source_type}")
    
    def process(self, source_type: str):
        source = self.create_source(source_type)
        data = source.read()
        return f"Processing: {data}"

# Usage
processor = DataProcessor()
print(processor.process("file"))  # Processing: Reading from file...
print(processor.process("api"))   # Processing: Reading from API...
```

#### Rust
```rust
trait DataSource {
    fn read(&self) -> String;
}

struct FileSource;
impl DataSource for FileSource {
    fn read(&self) -> String {
        "Reading from file...".into()
    }
}

struct DatabaseSource;
impl DataSource for DatabaseSource {
    fn read(&self) -> String {
        "Reading from database...".into()
    }
}

struct APISource;
impl DataSource for APISource {
    fn read(&self) -> String {
        "Reading from API...".into()
    }
}

struct DataProcessor;

impl DataProcessor {
    fn create_source(&self, source_type: &str) -> Box<dyn DataSource> {
        match source_type {
            "file" => Box::new(FileSource),
            "db" => Box::new(DatabaseSource),
            "api" => Box::new(APISource),
            _ => panic!("Unknown source"),
        }
    }
    
    fn process(&self, source_type: &str) -> String {
        let source = self.create_source(source_type);
        format!("Processing: {}", source.read())
    }
}

// Usage
let processor = DataProcessor;
println!("{}", processor.process("file"));
println!("{}", processor.process("api"));
```

### Common Use Cases
**General:**
- Payment processing where type depends on user choice at checkout
- Document export when format is selected by user
- Notification delivery based on user preferences

**IoT/ML:**
- Sensor drivers where hardware type is determined by configuration
- Communication protocols selected based on network availability
- ML model format decided by deployment environment

---

## Abstract Factory

### Problem
You need to create families of related objects that must work together.
> Creating incompatible combinations leads to errors. Like mixing furniture styles—a Windows button with Mac scrollbar looks wrong and may not work properly.

### Solution
Provide an interface for creating families of related objects.
> Each concrete factory produces a complete set of compatible products. Switch factories to switch entire product families at once.

### Code Examples

#### Python
```python
from abc import ABC, abstractmethod

# Abstract products
class Button(ABC):
    @abstractmethod
    def render(self): pass

class Checkbox(ABC):
    @abstractmethod
    def render(self): pass

# Windows family
class WindowsButton(Button):
    def render(self):
        return "Rendering Windows button"

class WindowsCheckbox(Checkbox):
    def render(self):
        return "Rendering Windows checkbox"

# Mac family
class MacButton(Button):
    def render(self):
        return "Rendering Mac button"

class MacCheckbox(Checkbox):
    def render(self):
        return "Rendering Mac checkbox"

# Abstract factory
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: pass
    
    @abstractmethod
    def create_checkbox(self) -> Checkbox: pass

# Concrete factories
class WindowsFactory(GUIFactory):
    def create_button(self):
        return WindowsButton()
    
    def create_checkbox(self):
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self):
        return MacButton()
    
    def create_checkbox(self):
        return MacCheckbox()

# Usage
def render_ui(factory: GUIFactory):
    button = factory.create_button()
    checkbox = factory.create_checkbox()
    print(button.render())
    print(checkbox.render())

# All components match
factory = WindowsFactory()  # or MacFactory()
render_ui(factory)
```

#### Rust
```rust
trait Button {
    fn render(&self) -> String;
}

trait Checkbox {
    fn render(&self) -> String;
}

// Windows family
struct WindowsButton;
impl Button for WindowsButton {
    fn render(&self) -> String {
        "Rendering Windows button".into()
    }
}

struct WindowsCheckbox;
impl Checkbox for WindowsCheckbox {
    fn render(&self) -> String {
        "Rendering Windows checkbox".into()
    }
}

// Mac family
struct MacButton;
impl Button for MacButton {
    fn render(&self) -> String {
        "Rendering Mac button".into()
    }
}

struct MacCheckbox;
impl Checkbox for MacCheckbox {
    fn render(&self) -> String {
        "Rendering Mac checkbox".into()
    }
}

// Abstract factory
trait GUIFactory {
    fn create_button(&self) -> Box<dyn Button>;
    fn create_checkbox(&self) -> Box<dyn Checkbox>;
}

// Concrete factories
struct WindowsFactory;
impl GUIFactory for WindowsFactory {
    fn create_button(&self) -> Box<dyn Button> {
        Box::new(WindowsButton)
    }
    fn create_checkbox(&self) -> Box<dyn Checkbox> {
        Box::new(WindowsCheckbox)
    }
}

struct MacFactory;
impl GUIFactory for MacFactory {
    fn create_button(&self) -> Box<dyn Button> {
        Box::new(MacButton)
    }
    fn create_checkbox(&self) -> Box<dyn Checkbox> {
        Box::new(MacCheckbox)
    }
}

// Usage
fn render_ui(factory: &dyn GUIFactory) {
    let button = factory.create_button();
    let checkbox = factory.create_checkbox();
    println!("{}", button.render());
    println!("{}", checkbox.render());
}

let factory: &dyn GUIFactory = &WindowsFactory;
render_ui(factory);
```

### Common Use Cases
**General:**
- UI themes where all components must match visual style
- Cross-platform apps where widgets adapt to the operating system
- Database access where connection, commands, and transactions belong to the same vendor

**IoT/ML:**
- Protocol stacks ensuring client and server use the same communication standard
- Cloud service abstraction where storage and compute come from one provider
- ML training pipelines where data loader, model, and optimizer work together

---

## Builder

### Problem
Creating complex objects with many optional parameters leads to unreadable constructors.
> The telescoping constructor problem makes code hard to read and error-prone. Like ordering a custom sandwich—easier to say "add this, add that" than listing everything upfront.

### Solution
Construct objects step-by-step using a builder interface.
> Build only what you need, in any order, with readable method chaining. Each method returns the builder for fluent interface.

### Code Examples

#### Python
```python
class HttpRequest:
    def __init__(self):
        self.method = "GET"
        self.url = ""
        self.headers = {}
        self.body = None
        self.timeout = 30
        self.retries = 3
    
    def __repr__(self):
        return f"Request({self.method} {self.url})"

class HttpRequestBuilder:
    def __init__(self):
        self._request = HttpRequest()
    
    def method(self, method: str):
        self._request.method = method
        return self
    
    def url(self, url: str):
        self._request.url = url
        return self
    
    def header(self, key: str, value: str):
        self._request.headers[key] = value
        return self
    
    def body(self, body: str):
        self._request.body = body
        return self
    
    def timeout(self, seconds: int):
        self._request.timeout = seconds
        return self
    
    def retries(self, count: int):
        self._request.retries = count
        return self
    
    def build(self) -> HttpRequest:
        return self._request

# Usage - fluent interface
request = (HttpRequestBuilder()
           .method("POST")
           .url("https://api.example.com/data")
           .header("Content-Type", "application/json")
           .header("Authorization", "Bearer token123")
           .body('{"temp": 25.5}')
           .timeout(10)
           .build())

print(request)  # Request(POST https://api.example.com/data)
```

#### Rust
```rust
#[derive(Debug, Default)]
struct HttpRequest {
    method: String,
    url: String,
    headers: std::collections::HashMap<String, String>,
    body: Option<String>,
    timeout: u32,
    retries: u8,
}

struct HttpRequestBuilder {
    request: HttpRequest,
}

impl HttpRequestBuilder {
    fn new() -> Self {
        Self {
            request: HttpRequest {
                method: "GET".into(),
                timeout: 30,
                retries: 3,
                ..Default::default()
            }
        }
    }
    
    fn method(mut self, method: &str) -> Self {
        self.request.method = method.into();
        self
    }
    
    fn url(mut self, url: &str) -> Self {
        self.request.url = url.into();
        self
    }
    
    fn header(mut self, key: &str, value: &str) -> Self {
        self.request.headers.insert(key.into(), value.into());
        self
    }
    
    fn body(mut self, body: &str) -> Self {
        self.request.body = Some(body.into());
        self
    }
    
    fn timeout(mut self, seconds: u32) -> Self {
        self.request.timeout = seconds;
        self
    }
    
    fn retries(mut self, count: u8) -> Self {
        self.request.retries = count;
        self
    }
    
    fn build(self) -> HttpRequest {
        self.request
    }
}

// Usage
let request = HttpRequestBuilder::new()
    .method("POST")
    .url("https://api.example.com/data")
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token123")
    .body(r#"{"temp": 25.5}"#)
    .timeout(10)
    .build();

println!("{:?}", request);
```

### Common Use Cases
**General:**
- Complex configuration objects avoiding constructors with many parameters
- Query building where clauses are added conditionally
- Test data creation with only relevant fields set

**IoT/ML:**
- Sensor setup defining pin, threshold, sampling rate, and filters step-by-step
- Neural network construction adding layers, activations, and regularization progressively
- Communication client configuration setting host, credentials, timeouts, and retry logic

---

## Prototype

### Problem
Creating new objects from scratch is expensive when initialization is complex.
> Recreating objects with database queries, file loading, or heavy computation wastes resources. Like photocopying—faster to copy than retype the entire document.

### Solution
Clone existing objects instead of creating new ones.
> Objects implement their own cloning logic, including deep copies of internal state. Modify the clone without affecting the original.

### Code Examples

#### Python
```python
from copy import deepcopy
from dataclasses import dataclass, field

@dataclass
class MLModelConfig:
    model_type: str
    layers: list = field(default_factory=list)
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    optimizer_params: dict = field(default_factory=dict)
    
    def clone(self):
        """Deep copy this configuration"""
        return deepcopy(self)

# Create base configuration
base_config = MLModelConfig(
    model_type="CNN",
    layers=[64, 128, 256, 512],
    learning_rate=0.001,
    optimizer_params={"momentum": 0.9, "weight_decay": 0.0001}
)

# Clone and modify for experiments
experiment1 = base_config.clone()
experiment1.learning_rate = 0.01
experiment1.batch_size = 64

experiment2 = base_config.clone()
experiment2.layers = [32, 64, 128]
experiment2.learning_rate = 0.0001

experiment3 = base_config.clone()
experiment3.optimizer_params["momentum"] = 0.95

# Each is independent
print(f"Base LR: {base_config.learning_rate}")      # 0.001
print(f"Exp1 LR: {experiment1.learning_rate}")      # 0.01
print(f"Exp2 layers: {experiment2.layers}")         # [32, 64, 128]
print(f"Base momentum: {base_config.optimizer_params['momentum']}")  # 0.9
```

#### Rust
```rust
#[derive(Clone, Debug)]
struct MLModelConfig {
    model_type: String,
    layers: Vec<u32>,
    learning_rate: f32,
    batch_size: u32,
    epochs: u32,
    optimizer_params: std::collections::HashMap<String, f32>,
}

impl MLModelConfig {
    fn new(model_type: &str) -> Self {
        Self {
            model_type: model_type.into(),
            layers: Vec::new(),
            learning_rate: 0.001,
            batch_size: 32,
            epochs: 100,
            optimizer_params: std::collections::HashMap::new(),
        }
    }
}

// Usage
let mut base_config = MLModelConfig::new("CNN");
base_config.layers = vec![64, 128, 256, 512];
base_config.optimizer_params.insert("momentum".into(), 0.9);
base_config.optimizer_params.insert("weight_decay".into(), 0.0001);

// Clone and modify
let mut experiment1 = base_config.clone();
experiment1.learning_rate = 0.01;
experiment1.batch_size = 64;

let mut experiment2 = base_config.clone();
experiment2.layers = vec![32, 64, 128];
experiment2.learning_rate = 0.0001;

let mut experiment3 = base_config.clone();
experiment3.optimizer_params.insert("momentum".into(), 0.95);

// Each is independent
println!("Base LR: {}", base_config.learning_rate);
println!("Exp1 LR: {}", experiment1.learning_rate);
println!("Exp2 layers: {:?}", experiment2.layers);
```

### Common Use Cases
**General:**
- Game character creation by copying templates and customizing attributes
- Document generation from templates with specific data filled in
- Test fixtures where base objects are cloned for each test

**IoT/ML:**
- Multiple sensor instances starting from one base configuration
- ML experiments varying one hyperparameter while keeping others constant
- Network packet generation from a template structure

---

## Quick Comparison

| Pattern | Creates | When to Use |
|---------|---------|-------------|
| **Factory Method** | One type at a time | Type varies at runtime |
| **Abstract Factory** | Related families | Need compatible sets |
| **Builder** | Complex objects | Many optional parameters |
| **Prototype** | By cloning | Creation is expensive |
| **Singleton** | Exactly one | Need single shared instance |

## Pattern Selection Guide

**Choose based on your problem:**

- Need one global instance? → **Singleton**
- Creating from scratch is slow? → **Prototype**  
- Many optional parameters? → **Builder**
- Need compatible sets? → **Abstract Factory**
- Type determined at runtime? → **Factory Method**
