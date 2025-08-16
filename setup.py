#!/usr/bin/env python3
"""
Setup script for IT Store Django Application
This script helps you get started with the application quickly.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def create_virtual_environment():
    """Create a virtual environment."""
    if os.path.exists('venv'):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command('python -m venv venv', 'Creating virtual environment')


def activate_virtual_environment():
    """Activate the virtual environment."""
    if os.name == 'nt':  # Windows
        activate_script = 'venv\\Scripts\\activate'
        python_path = 'venv\\Scripts\\python.exe'
        pip_path = 'venv\\Scripts\\pip.exe'
    else:  # Unix/Linux/macOS
        activate_script = 'venv/bin/activate'
        python_path = 'venv/bin/python'
        pip_path = 'venv/bin/pip'
    
    if not os.path.exists(python_path):
        print("❌ Virtual environment not found. Please run setup again.")
        return False, None, None
    
    return True, python_path, pip_path


def install_dependencies(pip_path):
    """Install Python dependencies."""
    return run_command(f'"{pip_path}" install -r requirements.txt', 'Installing dependencies')


def run_django_migrations(python_path):
    """Run Django migrations."""
    return run_command(f'"{python_path}" manage.py makemigrations', 'Creating database migrations') and \
           run_command(f'"{python_path}" manage.py migrate', 'Running database migrations')


def create_superuser(python_path):
    """Create a Django superuser."""
    print("🔄 Creating superuser...")
    print("   Please enter the following information:")
    
    # Set environment variables for non-interactive superuser creation
    env = os.environ.copy()
    env['DJANGO_SUPERUSER_EMAIL'] = 'admin@itstore.com'
    env['DJANGO_SUPERUSER_PASSWORD'] = 'admin123'
    env['DJANGO_SUPERUSER_FIRST_NAME'] = 'Admin'
    env['DJANGO_SUPERUSER_LAST_NAME'] = 'User'
    
    try:
        result = subprocess.run(
            f'"{python_path}" manage.py createsuperuser --noinput',
            shell=True, check=True, capture_output=True, text=True, env=env
        )
        print("✅ Superuser created successfully")
        print("   Email: admin@itstore.com")
        print("   Password: admin123")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create superuser: {e.stderr}")
        return False


def setup_sample_data(python_path):
    """Set up sample data for the application."""
    return run_command(f'"{python_path}" manage.py setup_sample_data', 'Setting up sample data')


def collect_static_files(python_path):
    """Collect static files."""
    return run_command(f'"{python_path}" manage.py collectstatic --noinput', 'Collecting static files')


def create_media_directories():
    """Create necessary media directories."""
    directories = [
        'media/products',
        'media/categories',
        'media/avatars',
        'media/documents'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Media directories created")
    return True


def create_env_file():
    """Create environment configuration file."""
    env_content = """# Django Settings
SECRET_KEY=django-insecure-change-this-in-production-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Email (Console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Static and Media files
STATIC_URL=/static/
MEDIA_URL=/media/
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Environment file (.env) created")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def print_success_message():
    """Print success message with next steps."""
    print("\n" + "="*60)
    print("🎉 IT Store Application Setup Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    
    print("\n2. Start the development server:")
    print("   python manage.py runserver")
    
    print("\n3. Open your browser and go to:")
    print("   http://127.0.0.1:8000")
    
    print("\n4. Login to admin panel:")
    print("   http://127.0.0.1:8000/admin")
    print("   Email: admin@itstore.com")
    print("   Password: admin123")
    
    print("\n📚 Documentation:")
    print("   - README.md: Project overview and setup instructions")
    print("   - Django admin: http://127.0.0.1:8000/admin")
    
    print("\n🔧 Development:")
    print("   - Create new products in the admin panel")
    print("   - Test user registration and login")
    print("   - Explore the store and support features")
    
    print("\n⚠️  Important Notes:")
    print("   - This is a development setup with DEBUG=True")
    print("   - Change SECRET_KEY in production")
    print("   - Use a proper database in production")
    print("   - Set up proper email backend in production")
    
    print("\n" + "="*60)


def main():
    """Main setup function."""
    print("🚀 IT Store Django Application Setup")
    print("="*40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Activate virtual environment and get paths
    success, python_path, pip_path = activate_virtual_environment()
    if not success:
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies(pip_path):
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        sys.exit(1)
    
    # Create media directories
    if not create_media_directories():
        sys.exit(1)
    
    # Run Django migrations
    if not run_django_migrations(python_path):
        sys.exit(1)
    
    # Create superuser
    if not create_superuser(python_path):
        sys.exit(1)
    
    # Setup sample data
    if not setup_sample_data(python_path):
        print("⚠️  Sample data setup failed, but you can continue")
    
    # Collect static files
    if not collect_static_files(python_path):
        print("⚠️  Static file collection failed, but you can continue")
    
    # Print success message
    print_success_message()


if __name__ == '__main__':
    main()
