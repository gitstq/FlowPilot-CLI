"""
FlowPilot CLI Commands Implementation
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

from flowpilot.core.parser import WorkflowParser
from flowpilot.core.engine import WorkflowEngine
from flowpilot.tui.monitor import WorkflowMonitor
from flowpilot.templates.manager import TemplateManager
from flowpilot.utils.logger import get_logger

logger = get_logger(__name__)


class Commands:
    """CLI command implementations"""
    
    def __init__(self):
        self.template_manager = TemplateManager()
    
    def run(self, workflow_file: str, variables: Optional[Dict[str, Any]] = None,
            monitor: bool = False, dry_run: bool = False,
            output_file: Optional[str] = None) -> int:
        """Execute a workflow"""
        try:
            # Parse workflow
            logger.info(f"📄 Loading workflow: {workflow_file}")
            workflow = WorkflowParser.parse_file(workflow_file)
            logger.info(f"✅ Workflow '{workflow.name}' loaded successfully")
            
            # Validate
            errors = WorkflowParser.validate_workflow(workflow)
            if errors:
                logger.error("❌ Workflow validation failed:")
                for error in errors:
                    logger.error(f"   - {error}")
                return 1
            
            if dry_run:
                logger.info("✅ Workflow validation passed (dry run)")
                return 0
            
            # Execute
            if monitor:
                # Run with TUI
                tui = WorkflowMonitor(workflow, variables)
                success = tui.run()
            else:
                # Run with simple output
                success = self._run_simple(workflow, variables)
            
            # Save output if requested
            if output_file:
                self._save_output(workflow, output_file)
            
            return 0 if success else 1
            
        except FileNotFoundError as e:
            logger.error(f"❌ {e}")
            return 1
        except Exception as e:
            logger.error(f"❌ Failed to run workflow: {e}")
            return 1
    
    def _run_simple(self, workflow, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Run workflow with simple console output"""
        engine = WorkflowEngine(workflow)
        
        def on_task_start(task):
            logger.info(f"🔄 Starting task: {task.name}")
        
        def on_task_end(task):
            status_icon = "✅" if task.status.value == "success" else "❌"
            logger.info(f"{status_icon} Task '{task.name}' {task.status.value}")
            if task.error:
                logger.error(f"   Error: {task.error[:200]}")
        
        engine.on_task_start = on_task_start
        engine.on_task_end = on_task_end
        
        logger.info(f"🚀 Executing workflow: {workflow.name}")
        success = engine.run(variables)
        
        # Print summary
        summary = engine.get_execution_summary()
        logger.info(f"\n📊 Execution Summary:")
        logger.info(f"   Status: {summary['status']}")
        logger.info(f"   Duration: {summary['duration']:.2f}s" if summary['duration'] else "   Duration: N/A")
        logger.info(f"   Tasks: {summary['successful']}/{summary['total_tasks']} successful")
        
        return success
    
    def validate(self, workflow_file: str) -> int:
        """Validate a workflow file"""
        try:
            logger.info(f"📄 Validating workflow: {workflow_file}")
            workflow = WorkflowParser.parse_file(workflow_file)
            
            errors = WorkflowParser.validate_workflow(workflow)
            
            if errors:
                logger.error("❌ Validation failed:")
                for error in errors:
                    logger.error(f"   - {error}")
                return 1
            
            logger.info(f"✅ Workflow '{workflow.name}' is valid!")
            logger.info(f"   Version: {workflow.version}")
            logger.info(f"   Tasks: {len(workflow.tasks)}")
            logger.info(f"   Description: {workflow.description or 'N/A'}")
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return 1
    
    def init(self, name: str, template: str = 'basic',
             output_file: Optional[str] = None) -> int:
        """Initialize a new workflow from template"""
        try:
            output_path = output_file or f"{name}.yml"
            
            if Path(output_path).exists():
                logger.error(f"❌ File already exists: {output_path}")
                return 1
            
            logger.info(f"📝 Creating workflow '{name}' from template '{template}'")
            
            content = self.template_manager.render_template(template, {
                'name': name,
                'description': f'Workflow: {name}'
            })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Created workflow file: {output_path}")
            logger.info(f"   Edit the file and run: flowpilot run {output_path}")
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Failed to create workflow: {e}")
            return 1
    
    def list_templates(self) -> int:
        """List available templates"""
        try:
            templates = self.template_manager.list_templates()
            
            logger.info("📋 Available Templates:\n")
            
            for name, info in templates.items():
                logger.info(f"  {name}")
                logger.info(f"     {info.get('description', 'No description')}")
                logger.info("")
            
            logger.info(f"Use 'flowpilot init <name> -t <template>' to create from template")
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Failed to list templates: {e}")
            return 1
    
    def monitor(self, workflow_file: str, 
                variables: Optional[Dict[str, Any]] = None) -> int:
        """Run workflow with TUI monitoring"""
        return self.run(
            workflow_file=workflow_file,
            variables=variables,
            monitor=True
        )
    
    def export(self, workflow_file: str, format: str,
               output_file: Optional[str] = None) -> int:
        """Export workflow to different format"""
        try:
            workflow = WorkflowParser.parse_file(workflow_file)
            
            if format == 'json':
                content = json.dumps(workflow.to_dict(), indent=2)
                default_output = workflow_file.replace('.yml', '.json').replace('.yaml', '.json')
            elif format == 'markdown':
                content = self._export_markdown(workflow)
                default_output = workflow_file.replace('.yml', '.md').replace('.yaml', '.md')
            else:
                logger.error(f"❌ Unsupported format: {format}")
                return 1
            
            output_path = output_file or default_output
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Exported to: {output_path}")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return 1
    
    def _export_markdown(self, workflow) -> str:
        """Export workflow as markdown documentation"""
        lines = [
            f"# {workflow.name}",
            "",
            f"**Version:** {workflow.version}",
            "",
            workflow.description or "",
            "",
            "## Tasks",
            "",
        ]
        
        for task in workflow.tasks:
            lines.append(f"### {task.name}")
            lines.append("")
            if task.description:
                lines.append(task.description)
                lines.append("")
            
            lines.append("**Steps:**")
            lines.append("")
            
            for i, step in enumerate(task.steps, 1):
                lines.append(f"{i}. **{step.name}**")
                lines.append(f"   ```bash")
                lines.append(f"   {step.command}")
                lines.append(f"   ```")
                if step.description:
                    lines.append(f"   {step.description}")
                lines.append("")
            
            if task.depends_on:
                lines.append(f"**Depends on:** {', '.join(task.depends_on)}")
                lines.append("")
        
        return '\n'.join(lines)
    
    def _save_output(self, workflow, output_file: str):
        """Save execution output to file"""
        engine = WorkflowEngine(workflow)
        summary = engine.get_execution_summary()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"💾 Results saved to: {output_file}")
    
    def show_template(self, template_name: str) -> int:
        """Show template content"""
        try:
            content = self.template_manager.get_template_content(template_name)
            print(content)
            return 0
        except Exception as e:
            logger.error(f"❌ Failed to show template: {e}")
            return 1
