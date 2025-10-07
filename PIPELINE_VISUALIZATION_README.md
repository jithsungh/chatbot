# 📊 Enhanced Inference Pipeline Visualization System

A comprehensive visualization and monitoring system for your chatbot's inference pipeline. This system provides beautiful console output, detailed timing analysis, step-by-step progress tracking, and performance metrics for every component of your pipeline.

## 🌟 Features

- **Beautiful Console Visualization**: Colored, step-by-step pipeline execution with emojis and clear formatting
- **Detailed Timing Analysis**: Precise timing for each pipeline step and overall performance metrics
- **Component-Specific Monitoring**: Specialized analysis for routing, context retrieval, prompt generation, LLM processing, and response formatting
- **Real-time Performance Statistics**: Live dashboard showing success rates, average times, and component health
- **Drop-in Replacement**: Easy integration with your existing pipeline code
- **Error Handling Visualization**: Clear display of errors and fallback mechanisms
- **Security Monitoring**: Track anonymization/deanonymization processes

## 🎯 What Gets Visualized

### Pipeline Steps

1. **🎯 Department Routing** - Query classification and routing analysis
2. **🔍 Context Retrieval** - Vector search and document retrieval metrics
3. **📚 History Management** - Conversation context and state tracking
4. **📝 Prompt Generation** - Template selection and content assembly
5. **🔒 Security Processing** - Anonymization and sanitization steps
6. **🤖 LLM Processing** - Model inference and response generation
7. **🎨 Response Formatting** - JSON parsing and structure validation

### Performance Metrics

- Step-by-step timing breakdown
- Success/failure rates by component
- Token usage and throughput analysis
- Context retrieval effectiveness
- Department routing accuracy
- Error rates and patterns

## 🚀 Quick Start

### Option 1: Enhanced Pipeline (Recommended)

Use the fully enhanced pipeline with comprehensive visualization:

```python
from src.inference.EnhancedPipeline import EnhancedPipeline

# Replace your existing pipeline
pipeline = EnhancedPipeline()

# Process queries - get beautiful visualization automatically
result = await pipeline.process_user_query("How do I reset my password?", "user123")
```

### Option 2: Monitored Pipeline (Drop-in Replacement)

Minimal changes to your existing code:

```python
from src.inference.MonitoredPipeline import MonitoredPipeline as Pipeline

# Use exactly like your original Pipeline - monitoring happens automatically
pipeline = Pipeline()
result = await pipeline.process_user_query("What is the HR policy?", "user456")

# Optional: Show live dashboard
pipeline.show_monitoring_dashboard()
```

### Option 3: Manual Integration with Existing Pipeline

Add monitoring to your current pipeline with minimal changes:

```python
from interactive_pipeline_monitor import track_query, log_step, complete_step, finish_query

async def your_existing_process_user_query(self, query: str, userid: str):
    # Start tracking
    query_id = track_query(query, userid)

    # Track each step
    step_idx = log_step(query_id, "Department Routing")
    dept = self.router.route_query(query)
    complete_step(query_id, step_idx, {"department": dept})

    # ... continue for other steps

    # Finish tracking
    finish_query(query_id, result)
    return result
```

## 🎮 Running the Demo

### Complete Visualization Demo

```bash
python visualization_demo.py
```

This runs a comprehensive demo showing:

- 5 different types of queries (HR, IT, Security, General)
- Complete pipeline visualization for each
- Performance statistics and analysis
- Component-specific metrics

### Interactive Monitor Demo

```bash
python interactive_pipeline_monitor.py
```

Shows the live monitoring system with simulated queries.

### Monitored Pipeline Test

```bash
python src/inference/MonitoredPipeline.py
```

Tests the drop-in replacement version with sample queries.

## 📁 Files Overview

### Core Visualization System

- **`PipelineVisualizer.py`** - Core visualization engine with colors and formatting
- **`EnhancedPipeline.py`** - Fully enhanced pipeline with comprehensive monitoring
- **`interactive_pipeline_monitor.py`** - Real-time monitoring system for easy integration

### Enhanced Components

- **`EnhancedRouter.py`** - Department router with detailed routing analysis
- **`EnhancedRetriever.py`** - Context retriever with search metrics and timing
- **`EnhancedPromptGenerator.py`** - Prompt generator with template and component analysis
- **`EnhancedLLMClient.py`** - LLM client with token usage and performance tracking
- **`EnhancedResponseFormatter.py`** - Response formatter with parsing method analysis

### Integration Options

- **`MonitoredPipeline.py`** - Drop-in replacement for your existing Pipeline.py
- **`visualization_demo.py`** - Comprehensive demonstration script

## 🎨 Customization

### Colors and Formatting

Modify colors in `PipelineVisualizer.py`:

```python
class Colors:
    ROUTER = '\\033[35m'      # Magenta for routing
    RETRIEVER = '\\033[36m'   # Cyan for retrieval
    HISTORY = '\\033[33m'     # Yellow for history
    # ... customize as needed
```

### Adding Custom Steps

Add monitoring to your own pipeline steps:

```python
from interactive_pipeline_monitor import log_step, complete_step

step_idx = log_step(query_id, "Your Custom Step", {"custom_data": value})
# ... your step logic ...
complete_step(query_id, step_idx, {"result_data": result})
```

### Performance Thresholds

Configure performance monitoring thresholds:

```python
# In the enhanced components, modify timing thresholds
if step_time > 1.0:  # Custom threshold
    print(f"{Colors.WARNING}⚠️ Step taking longer than expected{Colors.ENDC}")
```

## 📊 Understanding the Output

### Step Visualization

```
🔄 Department Routing...
🎯 Routing completed in 0.045s
✅ Department Routing completed in 0.045s

📊 Department Routing Analysis:
   Query (cleaned): what is the hr policy
   Detected Department: HR
   Keyword Matches: ['policy', 'hr']
   Routing Method: keyword
```

### Performance Summary

```
📋 PROCESSING SUMMARY
==================================================
Total Processing Time: 2.345s
Steps Completed: 7
Steps Failed: 0

Step Timing Breakdown:
✅ Department Routing: 0.045s
✅ Context Retrieval: 0.234s
✅ History Management: 0.012s
✅ Prompt Generation: 0.089s
✅ Security Anonymization: 0.023s
✅ LLM Processing: 1.823s
✅ Response Formatting: 0.119s
```

### Live Dashboard

```
📊 LIVE PIPELINE DASHBOARD
============================================================
Timestamp: 14:30:25
Active Queries: 0
Completed Queries: 15
Average Query Time: 2.156s
Overall Success Rate: 93.3%

Step Performance:
Department Routing: 0.042s avg, 100.0% success
Context Retrieval: 0.198s avg, 95.0% success
LLM Processing: 1.745s avg, 90.0% success
```

## 🔧 Integration with Your Existing Code

### Minimal Integration (Recommended)

Simply replace your Pipeline import:

```python
# Old code:
from src.inference.Pipeline import Pipeline

# New code:
from src.inference.MonitoredPipeline import MonitoredPipeline as Pipeline
```

### Advanced Integration

For more control, use the monitoring functions directly:

```python
from interactive_pipeline_monitor import track_query, log_step, complete_step, error_step, finish_query

class YourExistingPipeline:
    async def process_user_query(self, query: str, userid: str):
        query_id = track_query(query, userid)

        try:
            # Your existing routing code
            step_idx = log_step(query_id, "Department Routing")
            dept = self.router.route_query(query)
            complete_step(query_id, step_idx, {"department": dept})

            # ... rest of your pipeline steps

            finish_query(query_id, final_result)
            return final_result

        except Exception as e:
            error_step(query_id, step_idx, str(e))
            finish_query(query_id)
            raise
```

## 🚨 Requirements

### Python Dependencies

- `asyncio` - For async pipeline operations
- `time` - For timing analysis
- `json` - For data serialization
- `typing` - For type hints
- Your existing pipeline dependencies (chromadb, sentence-transformers, etc.)

### System Requirements

- Terminal with color support (most modern terminals)
- Python 3.7+ (for async/await support)
- Sufficient terminal width (80+ characters recommended)

## 🐛 Troubleshooting

### Colors Not Showing

If colors don't appear in your terminal:

```python
# Disable colors by modifying PipelineVisualizer.py
class Colors:
    # Set all colors to empty strings
    HEADER = ''
    OKBLUE = ''
    # ... etc
```

### Performance Impact

The visualization system is designed to be lightweight, but if you need to disable it:

```python
# In interactive_pipeline_monitor.py
monitor.monitoring_enabled = False  # Disable all monitoring
```

### Memory Usage

The system keeps the last 100 queries in memory. To reduce this:

```python
# In the monitoring classes, change the history limit
if len(self.history) > 50:  # Reduce from 100 to 50
    self.history.pop(0)
```

## 🎯 Performance Tips

1. **Use MonitoredPipeline for production** - It has minimal overhead
2. **Use EnhancedPipeline for development** - Full analysis but higher overhead
3. **Monitor specific steps** - Add monitoring only to steps you want to analyze
4. **Regular dashboard checks** - Use `show_dashboard()` to monitor system health

## 📈 Next Steps

1. **Integrate with your application** - Choose the integration method that works best
2. **Customize the visualization** - Modify colors and output format as needed
3. **Add custom metrics** - Extend the monitoring to track your specific KPIs
4. **Set up alerting** - Use the statistics to trigger alerts on performance issues
5. **Analyze patterns** - Use the historical data to identify optimization opportunities

## 🤝 Contributing

Feel free to extend this visualization system by:

- Adding new visualization components
- Improving the color schemes
- Adding export functionality for metrics
- Creating web-based dashboards
- Adding integration with monitoring tools

---

**Happy monitoring! 🎉**

Your pipeline processing will never be a black box again! 📊✨
