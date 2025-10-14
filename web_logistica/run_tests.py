#!/usr/bin/env python
"""
Script para ejecutar pruebas automatizadas del proyecto Logistica HR
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Agregar el directorio del proyecto al path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Configurar variables de entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistica_hr.settings_sqlite')


def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando: {command}")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def install_dependencies():
    """Instalar dependencias de testing"""
    print("Instalando dependencias de testing...")
    return run_command(
        "pip install -r requirements-testing.txt",
        "Instalando dependencias de testing"
    )


def run_unit_tests():
    """Ejecutar pruebas unitarias"""
    return run_command(
        "python -m pytest tests/unit/ -v --tb=short",
        "Ejecutando pruebas unitarias"
    )


def run_integration_tests():
    """Ejecutar pruebas de integración"""
    return run_command(
        "python -m pytest tests/integration/ -v --tb=short",
        "Ejecutando pruebas de integración"
    )


def run_e2e_tests():
    """Ejecutar pruebas end-to-end"""
    return run_command(
        "python -m pytest tests/e2e/ -v --tb=short",
        "Ejecutando pruebas end-to-end"
    )


def run_all_tests():
    """Ejecutar todas las pruebas"""
    return run_command(
        "python -m pytest tests/ -v --tb=short",
        "Ejecutando todas las pruebas"
    )


def run_tests_with_coverage():
    """Ejecutar pruebas con reporte de cobertura"""
    return run_command(
        "python -m pytest tests/ --cov=logistica_hr --cov-report=html --cov-report=term-missing",
        "Ejecutando pruebas con cobertura"
    )


def run_specific_tests(test_path):
    """Ejecutar pruebas específicas"""
    return run_command(
        f"python -m pytest {test_path} -v --tb=short",
        f"Ejecutando pruebas en {test_path}"
    )


def run_tests_by_marker(marker):
    """Ejecutar pruebas por marcador"""
    return run_command(
        f"python -m pytest -m {marker} -v --tb=short",
        f"Ejecutando pruebas marcadas como {marker}"
    )


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Ejecutar pruebas automatizadas de Logistica HR')
    parser.add_argument('--type', choices=['unit', 'integration', 'e2e', 'all'], 
                       default='all', help='Tipo de pruebas a ejecutar')
    parser.add_argument('--coverage', action='store_true', 
                       help='Incluir reporte de cobertura')
    parser.add_argument('--install', action='store_true', 
                       help='Instalar dependencias antes de ejecutar')
    parser.add_argument('--path', type=str, 
                       help='Ruta específica de pruebas a ejecutar')
    parser.add_argument('--marker', type=str, 
                       help='Marcador de pytest para filtrar pruebas')
    
    args = parser.parse_args()
    
    print("Logistica HR - Sistema de Pruebas Automatizadas")
    print("=" * 60)
    
    success = True
    
    # Instalar dependencias si se solicita
    if args.install:
        success = install_dependencies() and success
    
    # Ejecutar pruebas según el tipo especificado
    if args.path:
        success = run_specific_tests(args.path) and success
    elif args.marker:
        success = run_tests_by_marker(args.marker) and success
    elif args.coverage:
        success = run_tests_with_coverage() and success
    elif args.type == 'unit':
        success = run_unit_tests() and success
    elif args.type == 'integration':
        success = run_integration_tests() and success
    elif args.type == 'e2e':
        success = run_e2e_tests() and success
    else:  # all
        success = run_all_tests() and success
    
    # Mostrar resultado final
    print(f"\n{'='*60}")
    if success:
        print("¡Todas las pruebas se ejecutaron correctamente!")
    else:
        print("Algunas pruebas fallaron. Revisa los errores arriba.")
    print(f"{'='*60}")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
