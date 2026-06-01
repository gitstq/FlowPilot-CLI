"""
Tests for Workflow Parser
"""

import pytest
from flowpilot.core.parser import WorkflowParser
from flowpilot.models.workflow import Workflow, Task, Step


class TestWorkflowParser:
    """Test workflow parsing functionality"""
    
    def test_parse_simple_workflow(self):
        """Test parsing a simple workflow"""
        yaml_content = """
name: test-workflow
version: "1.0"
description: A test workflow

tasks:
  task1:
    description: First task
    steps:
      - name: step1
        run: echo "Hello"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        
        assert workflow.name == "test-workflow"
        assert workflow.version == "1.0"
        assert workflow.description == "A test workflow"
        assert len(workflow.tasks) == 1
        assert workflow.tasks[0].name == "task1"
        assert len(workflow.tasks[0].steps) == 1
    
    def test_parse_workflow_with_dependencies(self):
        """Test parsing workflow with task dependencies"""
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
  
  deploy:
    depends_on: [build]
    steps:
      - run: echo "Deploy"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        
        assert len(workflow.tasks) == 3
        
        setup_task = workflow.get_task("setup")
        build_task = workflow.get_task("build")
        deploy_task = workflow.get_task("deploy")
        
        assert setup_task.depends_on == []
        assert build_task.depends_on == ["setup"]
        assert deploy_task.depends_on == ["build"]
    
    def test_parse_workflow_with_env_and_vars(self):
        """Test parsing workflow with environment and variables"""
        yaml_content = """
name: env-test
version: "1.0"

env:
  GLOBAL_VAR: global_value

vars:
  workflow_var: workflow_value

tasks:
  task1:
    steps:
      - run: echo "Test"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        
        assert workflow.env["GLOBAL_VAR"] == "global_value"
        assert workflow.vars["workflow_var"] == "workflow_value"
    
    def test_parse_step_with_all_options(self):
        """Test parsing step with all options"""
        yaml_content = """
name: step-options-test
version: "1.0"

tasks:
  task1:
    steps:
      - name: complex_step
        run: echo "Hello"
        description: A complex step
        working_dir: /tmp
        env:
          STEP_VAR: step_value
        timeout: 30
        retry: 3
        retry_delay: 5
        ignore_error: true
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        step = workflow.tasks[0].steps[0]
        
        assert step.name == "complex_step"
        assert step.command == "echo \"Hello\""
        assert step.description == "A complex step"
        assert step.working_dir == "/tmp"
        assert step.env["STEP_VAR"] == "step_value"
        assert step.timeout == 30
        assert step.retry == 3
        assert step.retry_delay == 5
        assert step.ignore_error == True
    
    def test_validate_workflow_with_duplicate_tasks(self):
        """Test validation catches duplicate task names"""
        # YAML parser automatically merges duplicate keys, so we test with list format
        yaml_content = """
name: duplicate-test
version: "1.0"

tasks:
  - name: task1
    steps:
      - run: echo "First"
  - name: task1
    steps:
      - run: echo "Duplicate"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        errors = WorkflowParser.validate_workflow(workflow)
        
        assert len(errors) > 0
        assert any("Duplicate" in e for e in errors)
    
    def test_validate_workflow_with_missing_dependency(self):
        """Test validation catches missing dependencies"""
        yaml_content = """
name: missing-dep-test
version: "1.0"

tasks:
  task1:
    depends_on: [nonexistent]
    steps:
      - run: echo "Test"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        errors = WorkflowParser.validate_workflow(workflow)
        
        assert len(errors) > 0
        assert any("non-existent" in e.lower() for e in errors)
    
    def test_validate_workflow_with_circular_dependency(self):
        """Test validation catches circular dependencies"""
        yaml_content = """
name: circular-test
version: "1.0"

tasks:
  task1:
    depends_on: [task2]
    steps:
      - run: echo "Task 1"
  
  task2:
    depends_on: [task1]
    steps:
      - run: echo "Task 2"
"""
        
        workflow = WorkflowParser.parse_string(yaml_content)
        errors = WorkflowParser.validate_workflow(workflow)
        
        assert len(errors) > 0
        assert any("Circular" in e for e in errors)
    
    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML"""
        with pytest.raises(ValueError) as exc_info:
            WorkflowParser.parse_string("invalid: yaml: content: [")
        
        assert "Invalid YAML" in str(exc_info.value)
    
    def test_parse_workflow_without_name(self):
        """Test parsing workflow without required name field"""
        yaml_content = """
version: "1.0"
tasks:
  task1:
    steps:
      - run: echo "Test"
"""
        
        with pytest.raises(ValueError) as exc_info:
            WorkflowParser.parse_string(yaml_content)
        
        assert "name" in str(exc_info.value).lower()
