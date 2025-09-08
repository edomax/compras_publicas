#!/usr/bin/env python3
"""
Ejecutar migración automáticamente sin input interactivo
"""

from migrate_structure import ProjectMigrator

def main():
    print("🚀 Ejecutando migración automática...")
    migrator = ProjectMigrator()
    migrator.run_migration()

if __name__ == "__main__":
    main()