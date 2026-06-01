#!/usr/bin/env python3
"""
FlowPilot CLI - Main Entry Point
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flowpilot.cli.commands import Commands
from flowpilot.utils.logger import get_logger

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='flowpilot',
        description='🚀 FlowPilot-CLI - Lightweight Terminal Workflow Orchestration Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  flowpilot run workflow.yml              # Run a workflow
  flowpilot run workflow.yml -v KEY=value # Run with variables
  flowpilot validate workflow.yml         # Validate workflow syntax
  flowpilot init my-workflow              # Create new workflow from template
  flowpilot list                          # List available templates
  flowpilot monitor workflow.yml          # Run with TUI monitoring
  flowpilot export workflow.yml json      # Export workflow to JSON
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 1.0.0'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-error output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser(
        'run', 
        help='Execute a workflow',
        description='Run a workflow from YAML file'
    )
    run_parser.add_argument(
        'workflow_file',
        help='Path to workflow YAML file'
    )
    run_parser.add_argument(
        '--var', '-V',
        action='append',
        dest='variables',
        help='Set workflow variables (KEY=value)',
        metavar='KEY=value'
    )
    run_parser.add_argument(
        '--monitor', '-m',
        action='store_true',
        help='Enable TUI monitoring mode'
    )
    run_parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Validate without executing'
    )
    run_parser.add_argument(
        '--output', '-o',
        help='Save execution results to file (JSON format)'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate workflow syntax',
        description='Check workflow file for syntax errors'
    )
    validate_parser.add_argument(
        'workflow_file',
        help='Path to workflow YAML file'
    )
    
    # Init command
    init_parser = subparsers.add_parser(
        'init',
        help='Create new workflow from template',
        description='Initialize a new workflow file from template'
    )
    init_parser.add_argument(
        'name',
        help='Name for the new workflow'
    )
    init_parser.add_argument(
        '--template', '-t',
        default='basic',
        help='Template to use (default: basic)'
    )
    init_parser.add_argument(
        '--output', '-o',
        help='Output file path'
    )
    
    # List command
    list_parser = subparsers.add_parser(
        'list',
        help='List available templates',
        description='Show all available workflow templates'
    )
    
    # Monitor command
    monitor_parser = subparsers.add_parser(
        'monitor',
        help='Run workflow with TUI monitoring',
        description='Execute workflow with real-time TUI dashboard'
    )
    monitor_parser.add_argument(
        'workflow_file',
        help='Path to workflow YAML file'
    )
    monitor_parser.add_argument(
        '--var', '-V',
        action='append',
        dest='variables',
        help='Set workflow variables (KEY=value)',
        metavar='KEY=value'
    )
    
    # Export command
    export_parser = subparsers.add_parser(
        'export',
        help='Export workflow to different format',
        description='Export workflow to JSON or other formats'
    )
    export_parser.add_argument(
        'workflow_file',
        help='Path to workflow YAML file'
    )
    export_parser.add_argument(
        'format',
        choices=['json', 'yaml', 'markdown'],
        help='Export format'
    )
    export_parser.add_argument(
        '--output', '-o',
        help='Output file path'
    )
    
    # Template command
    template_parser = subparsers.add_parser(
        'template',
        help='Template management commands',
        description='Manage workflow templates'
    )
    template_subparsers = template_parser.add_subparsers(dest='template_command')
    
    template_show = template_subparsers.add_parser(
        'show',
        help='Show template content'
    )
    template_show.add_argument(
        'template_name',
        help='Name of the template'
    )
    
    return parser


def parse_variables(var_list: Optional[List[str]]) -> dict:
    """Parse variable strings into dictionary"""
    variables = {}
    if not var_list:
        return variables
    
    for var in var_list:
        if '=' not in var:
            logger.warning(f"Invalid variable format: {var}. Expected KEY=value")
            continue
        key, value = var.split('=', 1)
        variables[key.strip()] = value.strip()
    
    return variables


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    # Setup logging based on verbosity
    if parsed_args.verbose:
        os.environ['FLOWPILOT_LOG_LEVEL'] = 'DEBUG'
    elif parsed_args.quiet:
        os.environ['FLOWPILOT_LOG_LEVEL'] = 'ERROR'
    
    commands = Commands()
    
    try:
        if parsed_args.command == 'run':
            variables = parse_variables(parsed_args.variables)
            return commands.run(
                workflow_file=parsed_args.workflow_file,
                variables=variables,
                monitor=parsed_args.monitor,
                dry_run=parsed_args.dry_run,
                output_file=parsed_args.output
            )
        
        elif parsed_args.command == 'validate':
            return commands.validate(parsed_args.workflow_file)
        
        elif parsed_args.command == 'init':
            return commands.init(
                name=parsed_args.name,
                template=parsed_args.template,
                output_file=parsed_args.output
            )
        
        elif parsed_args.command == 'list':
            return commands.list_templates()
        
        elif parsed_args.command == 'monitor':
            variables = parse_variables(parsed_args.variables)
            return commands.monitor(
                workflow_file=parsed_args.workflow_file,
                variables=variables
            )
        
        elif parsed_args.command == 'export':
            return commands.export(
                workflow_file=parsed_args.workflow_file,
                format=parsed_args.format,
                output_file=parsed_args.output
            )
        
        elif parsed_args.command == 'template':
            if parsed_args.template_command == 'show':
                return commands.show_template(parsed_args.template_name)
            else:
                template_parser = argparse.ArgumentParser()
                template_parser.print_help()
                return 1
        
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        logger.info("\n⚠️  Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        if parsed_args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
