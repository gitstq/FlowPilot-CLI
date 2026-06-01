"""
Template Management
"""

import os
from pathlib import Path
from typing import Dict, Any
from string import Template


class TemplateManager:
    """Manage workflow templates"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "builtin"
        self._ensure_builtin_templates()
    
    def _ensure_builtin_templates(self):
        """Ensure builtin templates exist"""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic template
        basic_template = self.templates_dir / "basic.yml"
        if not basic_template.exists():
            basic_template.write_text(BASIC_TEMPLATE, encoding='utf-8')
        
        # Create ci-cd template
        ci_template = self.templates_dir / "ci-cd.yml"
        if not ci_template.exists():
            ci_template.write_text(CI_CD_TEMPLATE, encoding='utf-8')
        
        # Create data-pipeline template
        pipeline_template = self.templates_dir / "data-pipeline.yml"
        if not pipeline_template.exists():
            pipeline_template.write_text(DATA_PIPELINE_TEMPLATE, encoding='utf-8')
        
        # Create backup template
        backup_template = self.templates_dir / "backup.yml"
        if not backup_template.exists():
            backup_template.write_text(BACKUP_TEMPLATE, encoding='utf-8')
        
        # Create deploy template
        deploy_template = self.templates_dir / "deploy.yml"
        if not deploy_template.exists():
            deploy_template.write_text(DEPLOY_TEMPLATE, encoding='utf-8')
    
    def list_templates(self) -> Dict[str, Dict[str, str]]:
        """List available templates"""
        templates = {}
        
        for template_file in self.templates_dir.glob("*.yml"):
            name = template_file.stem
            content = template_file.read_text(encoding='utf-8')
            
            # Extract description from first comment
            description = "No description"
            for line in content.split('\n')[:5]:
                if line.startswith('#'):
                    description = line[1:].strip()
                    break
            
            templates[name] = {
                "description": description,
                "file": str(template_file),
            }
        
        return templates
    
    def render_template(self, template_name: str, variables: Dict[str, str]) -> str:
        """Render a template with variables"""
        template_file = self.templates_dir / f"{template_name}.yml"
        
        if not template_file.exists():
            available = ", ".join(self.list_templates().keys())
            raise ValueError(f"Template '{template_name}' not found. Available: {available}")
        
        content = template_file.read_text(encoding='utf-8')
        
        # Simple variable substitution
        template = Template(content)
        return template.safe_substitute(variables)
    
    def get_template_content(self, template_name: str) -> str:
        """Get raw template content"""
        template_file = self.templates_dir / f"{template_name}.yml"
        
        if not template_file.exists():
            raise ValueError(f"Template '{template_name}' not found")
        
        return template_file.read_text(encoding='utf-8')


# Builtin Templates

BASIC_TEMPLATE = '''# Basic workflow template
name: ${name}
version: "1.0"
description: ${description}

# Global environment variables
env:
  LOG_LEVEL: info

# Workflow variables
vars:
  greeting: "Hello, FlowPilot!"

tasks:
  setup:
    description: Setup environment
    steps:
      - name: check_environment
        run: echo "Environment check passed"
      - name: print_greeting
        run: echo "${greeting}"
  
  main:
    description: Main task
    depends_on: [setup]
    steps:
      - name: execute
        run: echo "Executing main task..."
      - name: complete
        run: echo "Task completed successfully!"
'''

CI_CD_TEMPLATE = '''# CI/CD Pipeline Template
name: ${name}
version: "1.0"
description: ${description}

env:
  NODE_ENV: production
  CI: "true"

tasks:
  install:
    description: Install dependencies
    steps:
      - name: clean
        run: rm -rf node_modules
      - name: npm_install
        run: npm ci
  
  lint:
    description: Run linter
    depends_on: [install]
    steps:
      - name: eslint
        run: npm run lint
        ignore_error: false
  
  test:
    description: Run tests
    depends_on: [install]
    steps:
      - name: unit_tests
        run: npm test
      - name: coverage
        run: npm run test:coverage
  
  build:
    description: Build application
    depends_on: [lint, test]
    steps:
      - name: clean_build
        run: rm -rf dist
      - name: build_app
        run: npm run build
      - name: verify_build
        run: test -d dist && echo "Build successful"
  
  deploy:
    description: Deploy to production
    depends_on: [build]
    steps:
      - name: deploy_app
        run: echo "Deploying to production..."
      - name: health_check
        run: echo "Running health checks..."
'''

DATA_PIPELINE_TEMPLATE = '''# Data Processing Pipeline Template
name: ${name}
version: "1.0"
description: ${description}

env:
  DATA_DIR: ./data
  OUTPUT_DIR: ./output

tasks:
  extract:
    description: Extract data from sources
    steps:
      - name: create_dirs
        run: mkdir -p ${DATA_DIR} ${OUTPUT_DIR}
      - name: download_data
        run: echo "Downloading data..."
      - name: verify_data
        run: echo "Data verification passed"
  
  transform:
    description: Transform and clean data
    depends_on: [extract]
    steps:
      - name: clean_data
        run: echo "Cleaning data..."
      - name: transform
        run: echo "Transforming data..."
      - name: validate
        run: echo "Validation complete"
  
  load:
    description: Load data to destination
    depends_on: [transform]
    steps:
      - name: prepare_load
        run: echo "Preparing for load..."
      - name: load_data
        run: echo "Loading data..."
      - name: verify_load
        run: echo "Load verification complete"
  
  report:
    description: Generate reports
    depends_on: [load]
    steps:
      - name: generate_report
        run: echo "Generating report..."
      - name: notify
        run: echo "Pipeline completed successfully!"
'''

BACKUP_TEMPLATE = '''# Backup Workflow Template
name: ${name}
version: "1.0"
description: ${description}

env:
  BACKUP_DIR: /backups
  RETENTION_DAYS: "7"

tasks:
  prepare:
    description: Prepare backup environment
    steps:
      - name: check_disk_space
        run: df -h | grep -E "(Filesystem|/$$)"
      - name: create_backup_dir
        run: mkdir -p ${BACKUP_DIR}/$(date +%Y%m%d)
  
  backup_files:
    description: Backup important files
    depends_on: [prepare]
    steps:
      - name: backup_configs
        run: echo "Backing up configuration files..."
      - name: backup_data
        run: echo "Backing up data..."
      - name: compress_backup
        run: echo "Compressing backup..."
  
  backup_database:
    description: Backup database
    depends_on: [prepare]
    steps:
      - name: dump_database
        run: echo "Creating database dump..."
      - name: compress_dump
        run: echo "Compressing database dump..."
  
  cleanup:
    description: Clean old backups
    depends_on: [backup_files, backup_database]
    steps:
      - name: remove_old
        run: echo "Removing backups older than ${RETENTION_DAYS} days..."
      - name: verify_cleanup
        run: echo "Cleanup complete"
  
  notify:
    description: Send notification
    depends_on: [cleanup]
    steps:
      - name: send_notification
        run: echo "Backup completed at $(date)"
'''

DEPLOY_TEMPLATE = '''# Deployment Workflow Template
name: ${name}
version: "1.0"
description: ${description}

env:
  DEPLOY_ENV: production
  APP_NAME: myapp

tasks:
  pre_deploy:
    description: Pre-deployment checks
    steps:
      - name: check_git_status
        run: echo "Checking git status..."
      - name: run_tests
        run: echo "Running pre-deployment tests..."
  
  build:
    description: Build application
    depends_on: [pre_deploy]
    steps:
      - name: install_deps
        run: echo "Installing dependencies..."
      - name: compile
        run: echo "Compiling application..."
      - name: package
        run: echo "Packaging application..."
  
  deploy:
    description: Deploy application
    depends_on: [build]
    steps:
      - name: backup_current
        run: echo "Backing up current version..."
      - name: upload_artifacts
        run: echo "Uploading new version..."
      - name: switch_version
        run: echo "Switching to new version..."
  
  post_deploy:
    description: Post-deployment verification
    depends_on: [deploy]
    steps:
      - name: health_check
        run: echo "Running health checks..."
      - name: smoke_tests
        run: echo "Running smoke tests..."
      - name: notify
        run: echo "Deployment to ${DEPLOY_ENV} completed!"
'''
