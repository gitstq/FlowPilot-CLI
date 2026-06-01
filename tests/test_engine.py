"""
Tests for Workflow Engine
"""

import pytest
import time
from flowpilot.core.parser import WorkflowParser
from flowpilot.core.engine import WorkflowEngine
from flowpilot.models.workflow import WorkflowStatus, TaskStatus


class TestWorkflowEngine:
    """Test workflow execution engine"""
    
    def test_simple_workflow_execution(self):
        """Test executing a simple workflow"""
        yaml_content = """
name: simple-test
version: "1.0"

tasks:
  task1:
    steps:
      - run: echo "Hello World"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        engine = WorkflowEngine(workflow)
        
        success = engine.run()
        
        assert success == True
        assert workflow.status == WorkflowStatus.SUCCESS
        assert workflow.tasks[0].status == TaskStatus.SUCCESS
    
    def test_workflow_with_dependencies(self):
        """Test workflow execution with task dependencies"""
        yaml_content = """
name: dependency-test
version: "1.0"

tasks:
  setup:
    steps:
      - run: echo "Setup"
  
  build:
    depends_on: [setup]
    steps:
      - run: echo "Build"
  
  test:
    depends_on: [build]
    steps:
      - run: echo "Test"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        engine = WorkflowEngine(workflow)
        
        execution_order = []
        
        def on_task_end(task):
            execution_order.append(task.name)
        
        engine.on_task_end = on_task_end
        success = engine.run()
        
        assert success == True
        assert execution_order == ["setup", "build", "test"]
    
    def test_workflow_with_failed_task(self):
        """Test workflow execution with a failing task"""
        yaml_content = """
name: failure-test
version: "1.0"

tasks:
  success_task:
    steps:
      - run: echo "Success"
  
  fail_task:
    steps:
      - run: exit 1
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        engine = WorkflowEngine(workflow)
        
        success = engine.run()
        
        assert success == False
        assert workflow.status == WorkflowStatus.FAILED
        assert workflow.get_task("fail_task").status == TaskStatus.FAILED
    
    def test_workflow_with_ignore_error(self):
        """Test workflow continues when step has ignore_error"""
        yaml_content = """
name: ignore-error-test
version: "1.0"

tasks:
  task1:
    steps:
      - name: failing_step
        run: exit 1
        ignore_error: true
      - name: next_step
        run: echo "Continued"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        engine = WorkflowEngine(workflow)
        
        success = engine.run()
        
        assert success == True
        assert workflow.status == WorkflowStatus.SUCCESS
    
    def test_workflow_with_variables(self):
        """Test workflow execution with variable substitution"""
        yaml_content = """
name: variable-test
version: "1.0"

vars:
  greeting: "Hello"
  target: "World"

tasks:
  task1:
    steps:
      - run: echo "${{ vars.greeting }}, ${{ vars.target }}!"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        engine = WorkflowEngine(workflow)
        
        success = engine.run()
        
        assert success == True
        # Check that output contains the resolved variables
        assert "Hello" in workflow.tasks[0].output
        assert "World" in workflow.tasks[0].output
    
    def test_workflow_execution_summary(self):
        """Test execution summary generation"""
        yaml_content = """
name: summary-test
version: "1.0"

tasks:
  task1:
    steps:
      - run: echo "Task 1"
  
  task2:
    steps:
      - run: echo "Task 2"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        engine = WorkflowEngine(workflow)
        
        engine.run()
        summary = engine.get_execution_summary()
        
        assert summary["workflow_name"] == "summary-test"
        assert summary["status"] == "success"
        assert summary["total_tasks"] == 2
        assert summary["successful"] == 2
        assert summary["failed"] == 0
        assert len(summary["tasks"]) == 2
    
    def test_workflow_duration_tracking(self):
        """Test workflow duration tracking"""
        yaml_content = """
name: duration-test
version: "1.0"

tasks:
  task1:
    steps:
      - run: sleep 0.1
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        engine = WorkflowEngine(workflow)
        
        engine.run()
        
        assert workflow.duration is not None
        assert workflow.duration > 0
        assert workflow.tasks[0].duration is not None
        assert workflow.tasks[0].duration > 0
