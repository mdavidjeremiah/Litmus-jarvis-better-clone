"""
Command-line interface for JARVIS
"""
import click
import sys
from pathlib import Path
# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from jarvis.core import JarvisCore
from jarvis.config.settings import Settings
@click.group()
def cli():
    """JARVIS AI Assistant CLI"""
    pass
@cli.command()
@click.option('--config', '-c', default='config/default_config.yaml', help='Config file path')
@click.option('--text-only', '-t', is_flag=True, help='Text-only mode')
def start(config, text_only):
    """Start JARVIS in voice or interactive mode"""
    settings = Settings.from_yaml(config)
    
    if text_only:
        settings.voice.enabled = False
    
    jarvis = JarvisCore(settings)
    
    try:
        if settings.voice.enabled:
            jarvis.run()
        else:
            jarvis.run_interactive()
    except KeyboardInterrupt:
        print("\nGoodbye!")
@cli.command()
@click.argument('command')
@click.option('--config', '-c', default='config/default_config.yaml')
def execute(command, config):
    """Execute a single command"""
    settings = Settings.from_yaml(config)
    settings.voice.enabled = False
    
    jarvis = JarvisCore(settings)
    response = jarvis.process_command_sync(command)
    print(response)
@cli.command()
def status():
    """Check JARVIS status"""
    settings = Settings.from_yaml('config/default_config.yaml')
    
    print("🤖 JARVIS Status")
    print("-" * 40)
    print(f"Voice: {'enabled' if settings.voice.enabled else 'disabled'}")
    print(f"Model: {settings.llm.model}")
    print(f"Data dir: {settings.data_dir}")
@cli.command()
def config():
    """Show current configuration"""
    settings = Settings.from_yaml('config/default_config.yaml')
    
    print("🤖 JARVIS Configuration")
    print("-" * 40)
    print(f"Wake word: {settings.voice.wake_word}")
    print(f"Language: {settings.voice.language}")
    print(f"LLM Model: {settings.llm.model}")
    print(f"Temperature: {settings.llm.temperature}")
    print(f"Cache path: {settings.web.cache_path}")
@cli.command()
@click.argument('url')
def cache(url):
    """Cache a URL for offline reading"""
    from jarvis.web.cache import WebCache
    
    cache = WebCache()
    success = cache.cache_url(url)
    if success:
        click.echo(f"✅ Cached: {url}")
    else:
        click.echo(f"❌ Failed to cache: {url}")
@cli.command()
@click.argument('query')
def search(query):
    """Search cached web content"""
    from jarvis.web.cache import WebCache
    
    cache = WebCache()
    results = cache.search(query)
    
    if results:
        click.echo(f"Found {len(results)} results:\n")
        for r in results:
            click.echo(f"📄 {r['title']}")
            click.echo(f"   {r['url']}\n")
    else:
        click.echo("No results found in cache.")
def main():
    cli()
if __name__ == '__main__':
    main()
